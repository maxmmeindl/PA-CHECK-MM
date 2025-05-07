# Instructions for Pushing to GitHub

Once you have access to your GitHub account, follow these steps to push this repository:

1. Create a new repository on GitHub named "PA-CHECK-MM" at https://github.com/maxmmeindl/PA-CHECK-MM

2. Generate a Personal Access Token (PAT) on GitHub:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with "repo" permissions
   - Copy the token

3. Push the repository using your PAT:
   ```
   git push -u origin main
   ```
   When prompted for credentials, use your GitHub username and the PAT as password.

4. Alternatively, you can update the remote URL to include your PAT:
   ```
   git remote set-url origin https://USERNAME:PAT@github.com/maxmmeindl/PA-CHECK-MM.git
   git push -u origin main
   ```

5. Verify the push was successful by visiting https://github.com/maxmmeindl/PA-CHECK-MM
