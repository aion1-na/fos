# Atlas

Owner: Data Product

Test command: `pnpm --filter @fos/atlas test`

Definition of done:

- Shows request status and metadata only until access is approved.
- Uses the data-service boundary rather than direct production dataset reads.
- Contains no real credentials, connector secrets, or dashboard tokens.
- Links every displayed production dataset to its dataset card and access policy.
