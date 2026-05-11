package protocols

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"sync"
	"time"

	"cc_hive/cc_empire/core"
)

type VocalCords struct {
	ModelID     string
	StoragePath string
	mu          sync.Mutex
}

func NewVocalCords(modelID string) *VocalCords {
	// Root is relative to the binary location in the Docker container
	storage := filepath.Join("media", "audio", modelID)
	_ = os.MkdirAll(storage, 0755)

	return &VocalCords{
		ModelID:     modelID,
		StoragePath: storage,
	}
}

// Speak converts text to speech using ElevenLabs API.
func (v *VocalCords) Speak(ctx context.Context, text string) ([]byte, error) {
	apiKey := core.Settings.ElevenLabsApiKey
	if apiKey == "" {
		return nil, fmt.Errorf("ElevenLabs API key missing")
	}

	url := fmt.Sprintf("https://api.elevenlabs.io/v1/text-to-speech/%s", core.Settings.ElevenLabsVoiceID)
	body, _ := json.Marshal(map[string]interface{}{
		"text":     text,
		"model_id": "eleven_monolingual_v1",
		"voice_settings": map[string]float64{
			"stability":        0.5,
			"similarity_boost": 0.75,
		},
	})

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(body))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Accept", "audio/mpeg")
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("xi-api-key", apiKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ElevenLabs API error: %d", resp.StatusCode)
	}

	return io.ReadAll(resp.Body)
}

// SaveAudio writes binary data to disk with a timestamped filename.
func (v *VocalCords) SaveAudio(audio []byte, label string) (string, error) {
	if len(audio) == 0 {
		return "", nil
	}

	timestamp := time.Now().Format("20060102_150405")
	filename := fmt.Sprintf("%s_%s.mp3", label, timestamp)
	path := filepath.Join(v.StoragePath, filename)

	err := os.WriteFile(path, audio, 0644)
	return path, err
}

// CleanupOldAudio removes files by age (days) and total directory size (MB).
func (v *VocalCords) CleanupOldAudio(days int, maxSizeMB int64) int {
	if !v.mu.TryLock() {
		return 0 // Already cleaning up
	}
	defer v.mu.Unlock()

	deletedCount := 0
	cutoff := time.Now().AddDate(0, 0, -days)

	entries, err := os.ReadDir(v.StoragePath)
	if err != nil {
		return 0
	}

	type fileInfo struct {
		path  string
		size  int64
		mtime time.Time
	}

	var remaining []fileInfo
	var totalSize int64

	// 1. Age-based cleanup
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".mp3" {
			continue
		}
		info, _ := entry.Info()
		fullPath := filepath.Join(v.StoragePath, entry.Name())

		if info.ModTime().Before(cutoff) {
			_ = os.Remove(fullPath)
			deletedCount++
		} else {
			totalSize += info.Size()
			remaining = append(remaining, fileInfo{fullPath, info.Size(), info.ModTime()})
		}
	}

	// 2. Size-based cleanup (Oldest first)
	sort.Slice(remaining, func(i, j int) bool {
		return remaining[i].mtime.Before(remaining[j].mtime)
	})

	limitBytes := maxSizeMB * 1024 * 1024
	for totalSize > limitBytes && len(remaining) > 0 {
		oldest := remaining[0]
		_ = os.Remove(oldest.path)
		totalSize -= oldest.size
		deletedCount++
		remaining = remaining[1:]
	}

	if deletedCount > 0 {
		log.Printf("Maintenance [%s]: Purged %d stale audio files.", v.ModelID, deletedCount)
	}
	return deletedCount
}
