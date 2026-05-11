package core

import (
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/joho/godotenv"
)

// Config stores all the settings for Cyber Chest.
type Config struct {
	Environment          string
	Debug                bool
	Port                 int
	Host                 string
	HostURL              string
	DatabaseURL          string
	OpenAIApiKey         string
	MongoVectorIndexName string
	ElevenLabsApiKey     string
	ElevenLabsVoiceID    string
	AzureKeyvaultURL     string
	RoyalUser            string
	RoyalPass            string
	StickyIPEndpoint     string
	MasterCryptoSeed     string
	AllowedOrigins       []string
}

var Settings *Config

// LoadConfig initializes the configuration singleton.
func LoadConfig() {
	// Load .env file if it exists
	_ = godotenv.Load(".env")

	Settings = &Config{
		Environment:          getEnv("ENVIRONMENT", "sandbox"),
		Debug:                getEnvAsBool("DEBUG", false),
		Port:                 getEnvAsInt("PORT", 8000),
		Host:                 getEnv("HOST", "0.0.0.0"),
		HostURL:              os.Getenv("HOST_URL"),
		DatabaseURL:          os.Getenv("DATABASE_URL"),
		OpenAIApiKey:         os.Getenv("OPENAI_API_KEY"),
		MongoVectorIndexName: getEnv("MONGODB_VECTOR_INDEX_NAME", "vector_index"),
		ElevenLabsApiKey:     os.Getenv("ELEVENLABS_API_KEY"),
		ElevenLabsVoiceID:    getEnv("ELEVENLABS_VOICE_ID", "21m0d2f4vM7BC8vhJBPp"),
		AzureKeyvaultURL:     os.Getenv("AZURE_KEYVAULT_URL"),
		RoyalUser:            os.Getenv("ROYAL_USER"),
		RoyalPass:            os.Getenv("ROYAL_PASS"),
		StickyIPEndpoint:     os.Getenv("STICKY_IP_ENDPOINT"),
		MasterCryptoSeed:     os.Getenv("MASTER_CRYPTO_SEED"),
		AllowedOrigins:       strings.Split(getEnv("ALLOWED_ORIGINS", "http://localhost:3000"), ","),
	}

	validateLaunch()
}

// validateLaunch runs the critical checks previously handled by Pydantic.
func validateLaunch() {
	var errors []string
	var warnings []string

	if Settings.DatabaseURL == "" {
		errors = append(errors, "DATABASE_URL is required")
	} else if !strings.HasPrefix(Settings.DatabaseURL, "mongodb") {
		errors = append(errors, "DATABASE_URL must begin with 'mongodb://' or 'mongodb+srv://'")
	}

	if Settings.OpenAIApiKey == "" {
		warnings = append(warnings, "OpenAI Key missing: NervousSystem will use fallback logic.")
	}

	if Settings.Environment == "production" {
		if Settings.Debug {
			errors = append(errors, "Debug mode cannot be enabled in production")
		}
		if Settings.RoyalUser == "" || Settings.RoyalPass == "" || Settings.StickyIPEndpoint == "" {
			warnings = append(warnings, "Production Proxy settings missing: IP integrity is at risk.")
		}
	}

	for _, w := range warnings {
		log.Printf("⚠️  Config Warning: %s", w)
	}

	if len(errors) > 0 {
		for _, e := range errors {
			log.Printf("❌ Config Error: %s", e)
		}
		// Only crash if not in a build environment
		if os.Getenv("RENDER_BUILD_STEP") != "true" {
			panic("Invalid configuration. Check logs for details.")
		}
	}
}

// Helper functions for environment parsing

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	valueStr := getEnv(key, "")
	if value, err := strconv.Atoi(valueStr); err == nil {
		return value
	}
	return defaultValue
}

func getEnvAsBool(key string, defaultValue bool) bool {
	valueStr := getEnv(key, "")
	if value, err := strconv.ParseBool(valueStr); err == nil {
		return value
	}
	return defaultValue
}

// IsProduction returns true if the environment is set to production.
func (c *Config) IsProduction() bool {
	return c.Environment == "production"
}
