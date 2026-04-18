# Install Claude Skills to Claude Code
# Usage: .\install-skills.ps1

$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillsDir = "$env:USERPROFILE\.claude\skills"

# Create skills directory if it doesn't exist
if (-not (Test-Path $skillsDir)) {
    Write-Host "Creating: $skillsDir"
    New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
}

$skillDomains = @(
    "engineering-team", "engineering", "product-team", "marketing-skill",
    "c-level-advisor", "project-management", "ra-qm-team", "business-growth",
    "finance", "agents", "commands", "standards", "templates"
)

$copied = 0
foreach ($domain in $skillDomains) {
    $sourcePath = "$sourceDir\$domain"
    $destPath = "$skillsDir\$domain"

    if ((Test-Path $sourcePath) -and ($sourcePath -ne $destPath)) {
        if (Test-Path $destPath) {
            Remove-Item -Recurse -Force $destPath | Out-Null
        }
        Copy-Item -Recurse -Force $sourcePath $destPath
        Write-Host "✓ $domain"
        $copied++
    }
}

Write-Host ""
Write-Host "Done! Installed $copied skills to:"
Write-Host "$skillsDir"
