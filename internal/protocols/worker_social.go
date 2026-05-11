package protocols

import (
	"cc_hive/cc_empire/core"
	"context"
	"fmt"
)

type WorkerSocialProtocol struct {
	ModelID       string
	NervousSystem *NervousSystem
	ProxiesActive bool
}

func NewWorkerSocialProtocol(modelID string) *WorkerSocialProtocol {
	return &WorkerSocialProtocol{
		ModelID:       modelID,
		NervousSystem: NewNervousSystem(modelID, "SFW"),
		// Safety Gate: Must be verified via proxy_handler logic later
		ProxiesActive: core.Settings.StickyIPEndpoint != "",
	}
}

type SocialAction struct {
	Platform string
	Text     string
	IsBanned bool
}

func (w *WorkerSocialProtocol) ExecuteSocialLoop(ctx context.Context, action SocialAction) (map[string]string, error) {
	if !w.ProxiesActive {
		return map[string]string{
			"status": "halt",
			"reason": "No active residential proxy detected.",
		}, nil
	}

	// Ensure AI never reveals identity
	vettedText := w.NervousSystem.Safety.Sanitize(action.Text)

	if action.IsBanned {
		// In production, trigger decommissioning via Executive here
		return map[string]string{
			"status": "self_destruct",
			"reason": fmt.Sprintf("Worker %s decommissioned due to ban on %s", w.ModelID, action.Platform),
		}, nil
	}

	return map[string]string{
		"status":         "success",
		"platform":       action.Platform,
		"vetted_content": vettedText,
	}, nil
}
