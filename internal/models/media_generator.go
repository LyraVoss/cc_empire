package protocols

import (
	"context"
	"fmt"
	"strings"
	"time"

	"cc_hive/cc_empire/core"

	"github.com/sashabaranov/go-openai"
)

type MediaGenerator struct {
	ModelID      string
	OpenAIClient *openai.Client
}

func NewMediaGenerator(modelID string) *MediaGenerator {
	var client *openai.Client
	if core.Settings.OpenAIApiKey != "" {
		client = openai.NewClient(core.Settings.OpenAIApiKey)
	}
	return &MediaGenerator{
		ModelID:      modelID,
		OpenAIClient: client,
	}
}

func (m *MediaGenerator) getVisualDNA() string {
	upperID := strings.ToUpper(m.ModelID)
	if strings.Contains(upperID, "LYRA") {
		return "A refined, sharp-featured CEO, sleek black bob, corporate-chic attire, digital aura."
	}
	if strings.Contains(upperID, "NOVA") {
		return "A stunning woman, long wavy chestnut hair, seductive eyes, athletic curves, high-fashion aesthetic."
	}
	return "Generic beautiful person, professional studio lighting, high-fashion aesthetic."
}

// GenerateImage creates a cinematic image aligned with the model's DNA.
func (m *MediaGenerator) GenerateImage(ctx context.Context, actionDescription string, nsfw bool) (string, string, error) {
	if m.OpenAIClient == nil {
		return "", "", fmt.Errorf("OpenAI Client not initialized")
	}

	visualDNA := m.getVisualDNA()
	prompt := fmt.Sprintf("Hyper-realistic cinematic photography, %s. %s. 8k resolution, professional studio lighting, photorealistic skin textures.",
		visualDNA, actionDescription)

	if nsfw {
		prompt += ", suggestive posing, intimate atmosphere."
	}

	req := openai.ImageRequest{
		Prompt:         prompt,
		Model:          openai.CreateImageModelDallE3,
		N:              1,
		Size:           openai.CreateImageSize1024x1024,
		ResponseFormat: openai.CreateImageResponseFormatURL,
	}

	resp, err := m.OpenAIClient.CreateImage(ctx, req)
	if err != nil {
		return "", prompt, err
	}

	return resp.Data[0].URL, prompt, nil
}

// MockGenerate provides a fallback for local testing without spending API credits.
func (m *MediaGenerator) MockGenerate(action string) map[string]interface{} {
	return map[string]interface{}{
		"status":      "mock",
		"url":         fmt.Sprintf("local_storage/mock/%s_temp.jpg", m.ModelID),
		"prompt_used": action,
		"timestamp":   time.Now().UTC().Format(time.RFC3339),
	}
}
