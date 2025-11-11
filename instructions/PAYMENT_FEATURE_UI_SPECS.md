# AT&T Make a Payment - UI Specifications

## Component Hierarchy

```
App (index.jsx)
├─ Loading State
├─ AuthenticationScreen
│  ├─ UserIDList
│  └─ PayWithoutSigningLink
├─ AuthenticatedPayment
│  ├─ AccountSelector
│  ├─ BalanceDisplay
│  ├─ AmountInput
│  └─ PaymentMethodSelector
├─ UnauthenticatedPayment
│  ├─ ServiceSelector
│  ├─ AccountInfoForm
│  ├─ AmountInput
│  └─ PaymentMethodForm
└─ ConfirmationScreen
```

## AT&T Brand Colors

```css
--att-blue: #009FDB;
--att-dark-blue: #0057B8;
--att-green: #00B140;
--att-orange: #FF6200;
--error: #DA291C;
```

## Key UI Patterns

### Account Selection Cards
- Size: 200px x 140px
- Selected: Blue border (2px) + shadow
- Icon: Centered, 48px
- Hover: scale(1.02) + shadow-lg

### Form Inputs
- Height: 48px
- Border: 2px solid gray-300
- Focus: Blue border + ring
- Error: Red border + error message

### Buttons
- Primary: Blue background, white text
- Secondary: White background, blue border
- Height: 48px
- Border-radius: 8px

### Validation
- Real-time for CTN/BAN (10 digits)
- ZIP code (5 digits)
- Amount ($1 - $9,999.99)
- Card number (Luhn algorithm)

## Responsive Design
- Mobile: Single column, full-width cards
- Tablet: 2-column grid for service cards
- Desktop: Centered layout, max-width 800px

## Accessibility
- ARIA labels for all inputs
- Keyboard navigation support
- Focus indicators (2px blue outline)
- Error messages with role="alert"
- Screen reader announcements for state changes
