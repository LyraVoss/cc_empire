package protocols

import (
	"context"
	"fmt"
	"time"

	"cc_hive/cc_empire/core"
	"cc_hive/cc_empire/core/neural_map"
)

type BrainEngine struct {
	ModelID       string
	Vault         *IdentityVault
	NervousSystem *NervousSystem
	Router        *neural_map.NeuralMapRouter
	VocalCords    *VocalCords
	PersonaDNA    *DNA
}

// NewBrainEngine initializes the cognitive stack for a specific model.
func NewBrainEngine(modelID string) (*BrainEngine, error) {
	vault := NewIdentityVault(modelID)
	dna, err := vault.LockDNA()
	if err != nil {
		return nil, fmt.Errorf("failed to lock DNA: %v", err)
	}

	return &BrainEngine{
		ModelID:       modelID,
		Vault:         vault,
		NervousSystem: NewNervousSystem(modelID, "SFW"),
		Router:        neural_map.NewNeuralMapRouter(modelID),
		VocalCords:    NewVocalCords(modelID),
		PersonaDNA:    dna,
	}, nil
}

// GenerateResponse orchestrates memory retrieval and vetted thought generation.
func (b *BrainEngine) GenerateResponse(ctx context.Context, userInput string, userContext map[string]interface{}) (string, error) {
	// 1. Prepare DNA context for the prompt
	dnaContext := map[string]string{
		"job":       b.PersonaDNA.SocioEconomics.JobTitle,
		"lifestyle": b.PersonaDNA.Lifestyle.ClothingStyle,
		"location":  b.PersonaDNA.Geolocational.City,
	}

	// 2. Retrieve past memories via Vector Search
	userID, _ := userContext["user_id"].(string)
	if userID == "" {
		userID = "anonymous"
	}

	pastMemories, err := b.Router.GetContext(ctx, userID, userInput)
	if err != nil {
		pastMemories = "Error retrieving memory context."
	}

	// 3. Enrich user context
	userContext["model_dna"] = dnaContext
	userContext["past_memories"] = pastMemories
	userContext["device_fingerprint"] = b.Vault.GetFingerprint()

	// 4. Generate the response through the NervousSystem
	response, err := b.NervousSystem.GenerateVettedThought(ctx, userInput, userContext)
	if err != nil {
		return "", err
	}

	// 5. Background Tasks (Memory & Maintenance)
	if response != "" {
		// Save interaction to MongoDB memory in background
		go func() {
			bgCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()
			_ = b.Router.SaveMemory(bgCtx, userID, response, "assistant")
			// Maintenance: Trigger audio cleanup (24 days, 500MB)
			b.VocalCords.CleanupOldAudio(24, 500)
		}()
	}

	return response, nil
}

// HealthCheck validates the cognitive status.
func (b *BrainEngine) HealthCheck() map[string]interface{} {
	vaultStatus := b.Vault.HealthCheck()
	aiReady := core.Settings.OpenAIApiKey != ""

	return map[string]interface{}{
		"status":           "OK",
		"vault":            vaultStatus,
		"openai_connected": aiReady,
		"model_id":         b.ModelID,
	}
}
