# Project Distribution

The ARK operator is distributed as a Helm chart for easy installation and configuration management.

## Helm Chart Distribution

Build the chart using the optional helm plugin:

```sh
kubebuilder edit --plugins=helm/v1-alpha
```

A chart will be generated under 'dist/chart', and users can obtain this solution from there.

**Note:** If you change the project, you need to update the Helm Chart using the same command above to sync the latest changes. Furthermore, if you create webhooks, you need to use the above command with the '--force' flag and manually ensure that any custom configuration previously added to 'dist/chart/values.yaml' or 'dist/chart/manager/manager.yaml' is manually re-applied afterwards.