# AT&T MCP Tools - Handoff Document

Per OpenAI Apps SDK guidelines, this document captures tool specifications for ChatGPT discovery and invocation.

---

## Tool 1: att-device-details

### Specification
| Field | Value |
|-------|-------|
| **Name** | `att-device-details` |
| **Title** | Shop Specific Device Model |
| **Description** | Use this when the user mentions a specific phone model by name (iPhone 17, iPhone 17 Pro, iPhone 17 Pro Max, Galaxy S25, S25 Ultra, etc.) and wants to see details, pricing, or purchase options. Returns device specifications, pricing, available colors, storage options, and trade-in offers. |
| **Returns Component** | Yes - `ui://widget/att-device-details.html` |
| **Auth Required** | No |

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "deviceId": {
      "type": "string",
      "enum": [
        "iphone-17-pro-max",
        "iphone-17-pro",
        "iphone-17",
        "samsung-s25-ultra",
        "samsung-s25-plus",
        "samsung-s25"
      ],
      "description": "Device identifier. Map user's device name to the enum value."
    }
  },
  "required": ["deviceId"]
}
```

### Output Schema
```json
{
  "deviceId": "string",
  "deviceName": "string",
  "price": "number",
  "colors": ["string"],
  "storage": ["string"],
  "tradeInValue": "number"
}
```

### Annotations
- `readOnlyHint`: true
- `destructiveHint`: false
- `openWorldHint`: false

### Test Prompts

#### ✅ Should Succeed (Direct)
- "I want to buy an iPhone 17 Pro Max"
- "Show me the Galaxy S25 Ultra"
- "What are the specs for the iPhone 17 Pro?"
- "I'm interested in the Samsung S25"

#### ✅ Should Succeed (Indirect)
- "I heard the new iPhone is out, can you show me?"
- "What's the price of the latest Samsung flagship?"

#### ❌ Should NOT Trigger (Negative)
- "Show me your phones" → should use att-products-carousel
- "What phones do you have?" → should use att-products-carousel
- "I need a new phone" (no model specified) → should use att-products-carousel

---

## Tool 2: att-store-locator

### Specification
| Field | Value |
|-------|-------|
| **Name** | `att-store-locator` |
| **Title** | Find AT&T Stores & Services |
| **Description** | Use this when the user wants to find AT&T store locations, get store hours, or visit a store in person. Returns an interactive map with store addresses, operating hours, available services, and directions. |
| **Returns Component** | Yes - `ui://widget/att-store-locator.html` |
| **Auth Required** | No |

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "location": {
      "type": "string",
      "description": "Location to search near. Can be a city name, ZIP code, or full address. If user says 'near me', omit this parameter."
    },
    "storeType": {
      "type": "string",
      "enum": ["retail", "authorized_retailer", "all"],
      "default": "all",
      "description": "Type of store to find. Defaults to 'all' if not specified."
    }
  }
}
```

### Output Schema
```json
{
  "location": "string | null",
  "storeType": "string",
  "stores": [
    {
      "name": "string",
      "address": "string",
      "hours": "string",
      "services": ["string"],
      "distance": "number"
    }
  ]
}
```

### Annotations
- `readOnlyHint`: true
- `destructiveHint`: false
- `openWorldHint`: false

### Test Prompts

#### ✅ Should Succeed (Direct)
- "Where is the nearest AT&T store?"
- "Find AT&T stores near 30092"
- "AT&T store hours in Atlanta"
- "I want to visit an AT&T store"

#### ✅ Should Succeed (Indirect)
- "I need to go somewhere to buy a phone in person"
- "Where can I get help with my AT&T service?"

#### ❌ Should NOT Trigger (Negative)
- "What phones do you have?" → should use att-products-carousel
- "Check if fiber is available" → should use att-fiber-coverage-checker

---

## Tool 3: att-fiber-coverage-checker

### Specification
| Field | Value |
|-------|-------|
| **Name** | `att-fiber-coverage-checker` |
| **Title** | Check Fiber & Internet Air Availability |
| **Description** | Use this when the user wants to check if AT&T Fiber or Internet Air (5G home internet) is available at their address. Returns a coverage map showing service availability and available plan options for the location. |
| **Returns Component** | Yes - `ui://widget/att-fiber-coverage-checker.html` |
| **Auth Required** | No |

### Input Schema
```json
{
  "type": "object",
  "properties": {
    "address": {
      "type": "string",
      "description": "Full street address to check for service availability. Include street, city, state, and ZIP code when provided by user."
    },
    "serviceType": {
      "type": "string",
      "enum": ["fiber", "internet_air", "all"],
      "default": "all",
      "description": "Type of internet service to check. 'fiber' for AT&T Fiber, 'internet_air' for 5G home internet, 'all' for both."
    }
  },
  "required": ["address"]
}
```

### Output Schema
```json
{
  "address": "string",
  "serviceType": "string",
  "availability": {
    "fiber": "boolean",
    "internetAir": "boolean"
  },
  "availablePlans": [
    {
      "name": "string",
      "speed": "string",
      "price": "number"
    }
  ]
}
```

### Annotations
- `readOnlyHint`: true
- `destructiveHint`: false
- `openWorldHint`: false

### Test Prompts

#### ✅ Should Succeed (Direct)
- "Is AT&T Fiber available at 123 Main St, Atlanta, GA 30301?"
- "Check internet availability at my address: 456 Oak Ave, Dallas, TX"
- "Can I get fiber internet at 4670 Avocet Dr, Peachtree Corners, GA 30092?"
- "Is Internet Air available in my area?"

#### ✅ Should Succeed (Indirect)
- "I want fast home internet, is it available where I live?"
- "What internet options do I have at my house?"

#### ❌ Should NOT Trigger (Negative)
- "Where is the AT&T store?" → should use att-store-locator
- "Show me internet plans" (no address) → may need to ask for address first

---

## Discovery Trigger Tokens

These keywords help ChatGPT auto-select the correct tool:

| Tool | Trigger Tokens |
|------|---------------|
| `att-device-details` | iphone, iphone 17, galaxy, samsung, buy phone, shop phone, phone details, device details, new phone, upgrade phone |
| `att-store-locator` | store, stores, att store, store near me, find store, locate store, store locator, nearest store, store hours |
| `att-fiber-coverage-checker` | fiber, att fiber, fiber internet, internet air, 5g home, home internet, check availability, coverage, is fiber available |

---

## Global Metadata

| Field | Value |
|-------|-------|
| **App Name** | AT&T Products & Services |
| **App Icon** | AT&T Globe logo |
| **MCP Endpoint** | `https://att-mcp.jpaulo.io/mcp` |
| **Assets Domain** | `https://att-mcp.jpaulo.io/assets/` |

---

## Error Handling

| Error Type | Response |
|------------|----------|
| Unknown tool | Return `isError: true` with message "Unknown tool: {name}" |
| Invalid deviceId | Model should map to valid enum or return validation error |
| Missing required address | Model should ask user for address before calling tool |

---

## Rate Limits

No rate limits currently implemented. All tools are read-only and do not require authentication.
