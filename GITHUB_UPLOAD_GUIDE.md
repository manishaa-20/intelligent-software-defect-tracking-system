# GitHub Upload Guide

## Option A — VS Code terminal (recommended)

Open the project folder in VS Code, then run:

```powershell
git init
git add .
git commit -m "Initial release: intelligent defect tracking dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/intelligent-software-defect-tracking-system.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and create the empty repository first.

## Create the repository on GitHub

1. Open GitHub.
2. Select **New repository**.
3. Repository name: `intelligent-software-defect-tracking-system`
4. Add a short description.
5. Choose Public if you want to showcase it.
6. Do not initialize another README, `.gitignore`, or license because this project already contains them.
7. Create the repository.
8. Run the commands above in the VS Code terminal.

## License

The project already contains `LICENSE` with the MIT License.

Before publishing, replace `Project Author` in `LICENSE` with the correct copyright holder name.

## Important dataset check

The supplied dataset contains fields such as Reporter, QA_Engineer and Assigned_To. If these are real people's names or confidential company data, do not publish the dataset publicly without permission. In that case, keep the repository private or publish only a sanitized/anonymized dataset.

## GitHub topics

Add:

- software-defect-tracking
- bug-tracking
- streamlit
- python
- plotly
- software-quality
- dashboard
- machine-learning
