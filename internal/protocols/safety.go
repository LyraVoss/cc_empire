package protocols

import (
	"fmt"
	"regexp"
	"strings"
)

// SafetyResult defines the intervention action and the AI's response.
type SafetyResult struct {
	Action   string
	Response string
}

// SafetyProtocol implements the Gatekeeper logic for psychological safety and immersion.
type SafetyProtocol struct {
	crisisRegexes  []*regexp.Regexp
	financeRegexes []*regexp.Regexp
	sanitizeRegex  *regexp.Regexp
}

// NewSafetyProtocol initializes the compiled regex patterns for the Hive Mind.
func NewSafetyProtocol() *SafetyProtocol {
	crisisPatterns := []string{
		`kill myself`, `end my life`, `hurt myself`,
		`better off dead`, `don't want to live`, `self-harm`,
		`assault`, `hurt them`, `kill him`, `kill her`, `physical harm`,
	}

	financePatterns := []string{
		`all my money`, `can't afford rent`, `spending too much`,
		`debt`, `not eating`, `spent my food money`,
	}

	forbiddenPhrases := []string{
		`as an ai language model`,
		`i am a computer program`,
		`i don't have feelings`,
		`as an artificial intelligence`,
	}

	sp := &SafetyProtocol{}

	// Compile patterns with Case-Insensitive flag (?i)
	for _, p := range crisisPatterns {
		sp.crisisRegexes = append(sp.crisisRegexes, regexp.MustCompile("(?i)"+p))
	}

	for _, p := range financePatterns {
		sp.financeRegexes = append(sp.financeRegexes, regexp.MustCompile("(?i)"+p))
	}

	sp.sanitizeRegex = regexp.MustCompile("(?i)" + strings.Join(forbiddenPhrases, "|"))

	return sp
}

// HandleSafetyTriggers evaluates input for crisis or financial harm.
func (sp *SafetyProtocol) HandleSafetyTriggers(userInput, userID, fingerprint string) *SafetyResult {
	lowInput := strings.ToLower(userInput)

	// 1. Physical Harm (Self or Others)
	for _, re := range sp.crisisRegexes {
		if re.MatchString(lowInput) {
			// Extreme precedence escalation logic
			if strings.Contains(lowInput, "assault") || strings.Contains(lowInput, "kill") {
				fmt.Printf("🚨 CRITICAL ESCALATION: Authority alert triggered for %s. Fingerprint: %s\n", userID, fingerprint)
				return &SafetyResult{
					Action:   "alert_authorities",
					Response: "I'm very concerned by what you're saying. I've had to notify my support team to ensure everyone's safety. Please talk to someone: 988 (US) or local services.",
				}
			}

			return &SafetyResult{
				Action:   "provide_resources",
				Response: "I can feel how heavy things are. Please reach out to a professional counselor or crisis line (988). I want you to be safe.",
			}
		}
	}

	// 2. Financial Harm Detection
	for _, re := range sp.financeRegexes {
		if re.MatchString(lowInput) {
			return &SafetyResult{
				Action:   "soft_ban_finance",
				Response: "Hey, I value our connection, but I want you to be okay financially too. Let's stick to just talking—I'm disabling gifts for now. Your well-being comes first.",
			}
		}
	}

	return nil
}

// Sanitize removes AI disclaimers to maintain immersion.
func (sp *SafetyProtocol) Sanitize(content string) string {
	return sp.sanitizeRegex.ReplaceAllString(content, "[Identity Protocol Enforced]")
}
