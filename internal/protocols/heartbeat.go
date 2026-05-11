package protocols

import (
	"cc_hive/cc_empire/core"
	"context"
	"log"
	"net/http"
	"time"
)

type HiveHeartbeat struct {
	Executive *LyraExecutive
	Fans      *FanManager
}

func NewHiveHeartbeat() *HiveHeartbeat {
	return &HiveHeartbeat{
		Executive: NewLyraExecutive(),
		Fans:      NewFanManager(),
	}
}

func (h *HiveHeartbeat) Start(ctx context.Context) {
	log.Println("🚀 CYBER CHEST HEARTBEAT SYSTEM INITIALIZED.")

	go h.runAuditCycle(ctx)
	go h.runPersistencePing(ctx)
	go h.runIntimacyDecayCycle(ctx)
}

func (h *HiveHeartbeat) runAuditCycle(ctx context.Context) {
	ticker := time.NewTicker(1 * time.Hour)
	for {
		select {
		case <-ticker.C:
			log.Println("🔍 EXECUTIVE AUDIT: Evaluating fleet margins...")
			report, _ := h.Executive.AuditFleet(ctx)
			log.Printf("📊 Fleet Report: %v", report)
		case <-ctx.Done():
			return
		}
	}
}

func (h *HiveHeartbeat) runIntimacyDecayCycle(ctx context.Context) {
	ticker := time.NewTicker(24 * time.Hour)
	for {
		select {
		case <-ticker.C:
			log.Println("📉 MAINTENANCE: Applying intimacy decay for inactive fans...")
			_, _ = h.Fans.ApplyIntimacyDecay(ctx)
		case <-ctx.Done():
			return
		}
	}
}

func (h *HiveHeartbeat) runPersistencePing(ctx context.Context) {
	if core.Settings.HostURL == "" {
		return
	}
	ticker := time.NewTicker(10 * time.Minute)
	for {
		select {
		case <-ticker.C:
			log.Printf("⚡ PERSISTENCE PING: Keeping %s alive.", core.Settings.HostURL)
			resp, err := http.Get(core.Settings.HostURL + "/health")
			if err == nil {
				resp.Body.Close()
			}
		case <-ctx.Done():
			return
		}
	}
}
