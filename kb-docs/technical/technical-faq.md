# CloudNest Technical Support FAQ

## Login Issues
If you can't log in, first confirm you're using the correct workspace URL (yourcompany.cloudnest.example, not the general cloudnest.example login). Password resets are sent to the email on file and expire after 1 hour. If SSO is enabled for your workspace, password login is disabled entirely — contact your workspace admin.

## API Rate Limits
The CloudNest API allows 100 requests/minute on Starter, 500 requests/minute on Pro, and custom limits on Enterprise. Exceeding the limit returns a 429 status code with a `Retry-After` header indicating how many seconds to wait. Rate limits are per API key, not per account, so creating multiple keys does not increase your effective limit — this is against our terms of service.

## Integration Errors
The most common integration error is `AUTH_401`, which means the API key is invalid or has been revoked. API keys are automatically revoked if unused for 90 days. The second most common is `WEBHOOK_TIMEOUT`, which occurs when your endpoint doesn't respond within 5 seconds — webhooks are not retried automatically unless you've enabled "Reliable Delivery" in Settings > Webhooks, which retries up to 3 times with exponential backoff.

## Data Export
Full account data exports can be requested from Settings > Data > Export. Exports are generated asynchronously and typically ready within 30 minutes for accounts under 10GB; larger accounts may take up to 24 hours. You'll receive an email with a download link valid for 7 days.

## Browser Compatibility
CloudNest's dashboard supports the latest two major versions of Chrome, Firefox, Safari, and Edge. Internet Explorer is not supported. Known issue: Safari users on macOS Sequoia may see a rendering glitch in the analytics chart view — a fix is planned but no ETA yet.

## Mobile App Sync Issues
If the mobile app shows stale data, try Settings > Force Sync within the app. Sync typically happens every 15 minutes automatically. Persistent sync failures are usually caused by an expired session — logging out and back in resolves this in most cases.

## Two-Factor Authentication
2FA can be enabled from Settings > Security. We support authenticator apps (TOTP) and SMS, though SMS is being deprecated for new setups due to security concerns — authenticator apps are recommended. Lost access to your 2FA device requires identity verification via support, which takes 1-2 business days.

## Custom Domains
Enterprise customers can set up a custom domain (e.g. app.yourcompany.com) by adding a CNAME record pointing to custom.cloudnest.example, then verifying ownership in Settings > Domains. SSL certificates are provisioned automatically within 24 hours of verification.
