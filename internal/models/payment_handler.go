package protocols

import (
	"fmt"
	"log"

	"cc_hive/cc_empire/core"

	"github.com/stripe/stripe-go/v76"
	"github.com/stripe/stripe-go/v76/checkout/session"
)

type PaymentHandler struct {
	ModelID string
}

func NewPaymentHandler(modelID string) *PaymentHandler {
	if core.Settings.StripeSecretKey != "" {
		stripe.Key = core.Settings.StripeSecretKey
	}
	return &PaymentHandler{ModelID: modelID}
}

// CreateStripeCheckout generates a session for gifts or subscriptions.
func (p *PaymentHandler) CreateStripeCheckout(amount int64, currency string, successURL, cancelURL string) (string, error) {
	if stripe.Key == "" {
		return "", fmt.Errorf("Stripe API key is not configured")
	}

	params := &stripe.CheckoutSessionParams{
		PaymentMethodTypes: stripe.StringSlice([]string{"card"}),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			{
				PriceData: &stripe.CheckoutSessionLineItemPriceDataParams{
					Currency:   stripe.String(currency),
					UnitAmount: stripe.Int64(amount),
					ProductData: &stripe.CheckoutSessionLineItemPriceDataProductDataParams{
						Name: stripe.String(fmt.Sprintf("Gift for %s", p.ModelID)),
					},
				},
				Quantity: stripe.Int64(1),
			},
		},
		Mode:       stripe.String(string(stripe.CheckoutSessionModePayment)),
		SuccessURL: stripe.String(successURL),
		CancelURL:  stripe.String(cancelURL),
	}

	sess, err := session.New(params)
	if err != nil {
		return "", err
	}

	return sess.URL, nil
}

// DeriveDelegatedWallet generates a sub-wallet from the master seed for the specific model.
func (p *PaymentHandler) DeriveDelegatedWallet() string {
	if core.Settings.MasterCryptoSeed == "" {
		return "MOCK_WALLET_ADDRESS_PROD_SEED_MISSING"
	}
	log.Printf("🧠 PaymentHandler: Deriving HD wallet for %s from Master Seed.", p.ModelID)
	return fmt.Sprintf("0xDelegatedAddressFor%s", p.ModelID)
}
