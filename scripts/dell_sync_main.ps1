$ErrorActionPreference = "Stop"

$branch = git rev-parse --abbrev-ref HEAD
if ($LASTEXITCODE -ne 0) {
    throw "Failed to detect current git branch."
}

git diff --quiet
$workTreeDirty = $LASTEXITCODE -ne 0
git diff --cached --quiet
$indexDirty = $LASTEXITCODE -ne 0

if ($workTreeDirty -or $indexDirty) {
    throw "Refusing to sync: Dell working tree is not clean."
}

if ($branch.Trim() -ne "main") {
    git checkout main
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to switch to main."
    }
}

git fetch origin
if ($LASTEXITCODE -ne 0) {
    throw "Failed to fetch origin."
}

git reset --hard origin/main
if ($LASTEXITCODE -ne 0) {
    throw "Failed to reset to origin/main."
}

Write-Host "Dell runtime is now exactly synced to origin/main."
