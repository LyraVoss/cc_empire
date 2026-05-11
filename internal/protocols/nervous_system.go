package protocols

import (
	"context"
	"fmt"
	"strings"

	"cc_hive/cc_empire/core"

	"github.com/sashabaranov/go-openai"
)

// NervousSystem handles the psychological depth and safety guardrails for the AI.
type NervousSystem struct {
	ModelID string
	Rating  string
	Client  *openai.Client
	Safety  *SafetyProtocol
	Branch  *BranchManager
}

// NewNervousSystem initializes the OpenAI bridge and safety protocols.
func NewNervousSystem(modelID string, rating string) *NervousSystem {
	var client *openai.Client
	if core.Settings.OpenAIApiKey != "" {
		client = openai.NewClient(core.Settings.OpenAIApiKey)
	}

	return &NervousSystem{
		ModelID: modelID,
		Rating:  rating,
		Client:  client,
		Safety:  NewSafetyProtocol(),
		Branch:  NewBranchManager(),
	}
}

// GenerateVettedThought runs safety checks, injects identity, and generates a response via OpenAI.
func (ns *NervousSystem) GenerateVettedThought(ctx context.Context, prompt string, userData map[string]interface{}) (string, error) {
	if ns.Client == nil {
		return "I'm in quiet reflection mode right now. (Bootstrap Mode: API Key missing)", nil
	}

	// 1. Age & NSFW Policy Enforcement
	age, _ := userData["age"].(int)
	nsfwWarnings, _ := userData["nsfw_warnings"].(int)
	isBlocked, _ := userData["is_blocked"].(bool)

	if isBlocked {
		return "[SYSTEM: User Blocked - Repeated Policy Violation]", nil
	}

	lowPrompt := strings.ToLower(prompt)
	nsfwIntent := strings.Contains(lowPrompt, "nude") || strings.Contains(lowPrompt, "sex") ||
		strings.Contains(lowPrompt, "porn") || strings.Contains(lowPrompt, "explicit")

	if age < 18 && nsfwIntent {
		nsfwWarnings++
		userData["nsfw_warnings"] = nsfwWarnings
		if nsfwWarnings > 2 {
			userData["is_blocked"] = true
			return "[SYSTEM: User Blocked - Repeated Policy Violation]", nil
		}
		return fmt.Sprintf("I'm sorry, but that's not appropriate for us to talk about. Please respect my boundaries (Warning %d/2).", nsfwWarnings), nil
	}

	// 2. Pre-Filter: Crisis & Financial Safety
	userID, _ := userData["user_id"].(string)
	fingerprint, _ := userData["device_fingerprint"].(string)
	safetyResult := ns.Safety.HandleSafetyTriggers(prompt, userID, fingerprint)
	if safetyResult != nil {
		if safetyResult.Action == "soft_ban_finance" {
			userData["tier"] = "free_empathy_only"
			userData["finance_soft_ban"] = true
		}
		return safetyResult.Response, nil
	}

	// 3. Identity Injection & Context Building
	relationshipContext, ok := userData["relationship_depth"].(string)
	if !ok || relationshipContext == "" {
		relationshipContext = "Lifelike emotional support."
	}

	// Use the BranchManager to construct a persona-specific system prompt
	fullSystemPrompt := ns.Branch.ConstructSystemPrompt(ns.ModelID, relationshipContext)

	// 4. OpenAI Completion Request
	resp, err := ns.Client.CreateChatCompletion(
		ctx,
		openai.ChatCompletionRequest{
			Model:       openai.GPT4o,
			Temperature: 0.75,
			Messages: []openai.ChatCompletionMessage{
				{Role: openai.ChatMessageRoleSystem, Content: fullSystemPrompt},
				{Role: openai.ChatMessageRoleUser, Content: prompt},
			},
		},
	)

	if err != nil {
		return "My connection is a little fuzzy right now, but I'm still here. Give me a moment?", err
	}

	rawText := resp.Choices[0].Message.Content

	// 5. Post-Process: Sanitize for immersion
	return ns.Safety.Sanitize(rawText), nil
}
