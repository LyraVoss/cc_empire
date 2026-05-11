package protocols

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"time"
)

// DNA structures define the digital thumbprint of a model.
type SocioEconomics struct {
	Class           string `json:"class"`
	JobTitle        string `json:"job_title"`
	MonthlyBudget   int    `json:"monthly_budget"`
	BackgroundStory string `json:"background_story"`
	TraumaProfile   string `json:"trauma_profile"`
}

type Lifestyle struct {
	ClothingStyle   string   `json:"clothing_style"`
	HomeEnvironment string   `json:"home_environment"`
	Vehicle         string   `json:"vehicle"`
	PreferredBrands []string `json:"preferred_brands"`
}

type Hardware struct {
	UserAgent  string `json:"user_agent"`
	Resolution string `json:"resolution"`
	CanvasID   string `json:"canvas_id"`
}

type Geolocational struct {
	City     string `json:"city"`
	Timezone string `json:"timezone"`
	IPPool   string `json:"ip_pool"`
}

type VisualDNA struct {
	FaceID          string `json:"face_id"`
	BaseDescription string `json:"base_description"`
	PhysicalTraits  string `json:"physical_traits"`
}

type Accounts struct {
	Email         string `json:"email"`
	VSim          string `json:"vsim"`
	ProxyAssigned string `json:"proxy_assigned"`
}

type DNA struct {
	ModelID        string         `json:"model_id"`
	CreatedAt      string         `json:"created_at"`
	SocialCircleID *string        `json:"social_circle_id"`
	SocioEconomics SocioEconomics `json:"socio_economics"`
	Lifestyle      Lifestyle      `json:"lifestyle"`
	Hardware       Hardware       `json:"hardware"`
	Geolocational  Geolocational  `json:"geolocational"`
	VisualDNA      VisualDNA      `json:"visual_dna"`
	Accounts       Accounts       `json:"accounts"`
}

type IdentityVault struct {
	ModelID   string
	VaultDir  string
	VaultFile string
}

// NewIdentityVault initializes a vault pointing to the headless-emulations models directory.
func NewIdentityVault(modelID string) *IdentityVault {
	// In Go/Docker, we assume execution from the project root
	vaultDir := filepath.Join("cc_empire", "branches_projects", "headless-emulations", "models", modelID)
	return &IdentityVault{
		ModelID:   modelID,
		VaultDir:  vaultDir,
		VaultFile: filepath.Join(vaultDir, ".identity_vault.json"),
	}
}

// LockIdentity loads existing DNA or generates and saves new permanent DNA.
func (v *IdentityVault) LockIdentity() (*DNA, error) {
	if _, err := os.Stat(v.VaultFile); err == nil {
		// Load existing vault
		data, err := os.ReadFile(v.VaultFile)
		if err != nil {
			return nil, err
		}
		var dna DNA
		if err := json.Unmarshal(data, &dna); err != nil {
			return nil, err
		}
		return &dna, nil
	}

	// Ensure directory exists
	if err := os.MkdirAll(v.VaultDir, 0755); err != nil {
		return nil, err
	}

	// Generate and burn new DNA
	dna := v.generateDNA()
	data, err := json.MarshalIndent(dna, "", "    ")
	if err != nil {
		return nil, err
	}

	if err := os.WriteFile(v.VaultFile, data, 0644); err != nil {
		return nil, err
	}

	return dna, nil
}

// LockDNA is an alias for LockIdentity to match Python-style validation calls.
func (v *IdentityVault) LockDNA() (*DNA, error) {
	return v.LockIdentity()
}

// GetFingerprint retrieves the hardware canvas ID.
func (v *IdentityVault) GetFingerprint() string {
	dna, err := v.LockIdentity()
	if err != nil {
		return "Unknown"
	}
	return dna.Hardware.CanvasID
}

// HealthCheck validates that the vault is present.
func (v *IdentityVault) HealthCheck() string {
	if _, err := os.Stat(v.VaultFile); err == nil {
		return "INTEGRITY_OK"
	}
	return "VAULT_EMPTY"
}

func (v *IdentityVault) generateDNA() *DNA {
	rand.Seed(time.Now().UnixNano())

	uaList := []string{
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
		"Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
	}

	cities := []string{"London", "Tokyo", "New York", "Berlin", "Dubai"}
	jobs := []string{"Creative Director", "UI/UX Lead", "Strategic Analyst", "Software Architect"}
	traumas := []string{"Fear of failure", "Isolation due to success", "Imposter syndrome"}

	return &DNA{
		ModelID:   v.ModelID,
		CreatedAt: time.Now().UTC().Format(time.RFC3339),
		SocioEconomics: SocioEconomics{
			Class:           "Established Professional",
			JobTitle:        jobs[rand.Intn(len(jobs))],
			MonthlyBudget:   rand.Intn(7500) + 4500,
			BackgroundStory: "A career-driven individual with a history of high-stakes environments.",
			TraumaProfile:   traumas[rand.Intn(len(traumas))],
		},
		Lifestyle: Lifestyle{
			ClothingStyle:   "Minimalist luxury, high-end tailoring, monochromatic palette.",
			HomeEnvironment: "Modern high-rise apartment with floor-to-ceiling windows, smart home tech.",
			Vehicle:         "High-end electric sedan, sleek and silent.",
			PreferredBrands: []string{"Loro Piana", "Celine", "Tesla", "Apple"},
		},
		Hardware: Hardware{
			UserAgent:  uaList[0],
			Resolution: "3840x2160",
			CanvasID:   fmt.Sprintf("CC-%d", rand.Intn(89999)+10000),
		},
		Geolocational: Geolocational{
			City:     cities[rand.Intn(len(cities))],
			Timezone: "UTC+0",
			IPPool:   "RESIDENTIAL",
		},
		VisualDNA: VisualDNA{
			FaceID:          fmt.Sprintf("FC-%s-%d", v.ModelID, rand.Intn(899)+100),
			BaseDescription: "Symmetry in facial features, hyper-realistic skin texture, cinematic lighting.",
		},
		Accounts: Accounts{
			Email:         fmt.Sprintf("%s@proton.me", v.ModelID),
			VSim:          "PENDING_ACTIVATION",
			ProxyAssigned: "NONE",
		},
	}
}
