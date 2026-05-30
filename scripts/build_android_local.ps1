param(
    [string]$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path,
    [string]$RenpySdk = $env:RENPY_SDK,
    [string]$JavaHome = $env:JAVA_HOME,
    [string]$Destination = ''
)

if (-not $RenpySdk) {
    $RenpySdk = 'C:\Repos\AI\tools\renpy-8.5.3-sdk'
}

if (-not $JavaHome) {
    $JavaHome = 'C:\Repos\AI\tools\jdk-21\jdk-21.0.11+10'
}

if (-not $Destination) {
    $Destination = Join-Path $RepoRoot 'builds\android'
}

$project = Join-Path $RepoRoot 'Sam And Em'
$renpy = Join-Path $RenpySdk 'renpy.exe'
$launcher = Join-Path $RenpySdk 'launcher'
$emailScript = Join-Path $RepoRoot 'scripts\send_build_email.py'

if (-not (Test-Path -LiteralPath $renpy)) {
    throw "Ren'Py SDK not found at $renpy. Set RENPY_SDK or pass -RenpySdk."
}

if (-not (Test-Path -LiteralPath (Join-Path $JavaHome 'bin\java.exe'))) {
    throw "JDK not found at $JavaHome. Set JAVA_HOME or pass -JavaHome."
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null

$env:JAVA_HOME = $JavaHome
$env:Path = (Join-Path $JavaHome 'bin') + ';' + $env:Path

Write-Host 'Running Ren''Py lint...'
& $renpy $project lint
$lintExitCode = if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE }
if ($lintExitCode -ne 0) {
    throw "Ren'Py lint failed with exit code $lintExitCode."
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stdoutLog = Join-Path $Destination "android-build-local-$stamp.stdout.log"
$stderrLog = Join-Path $Destination "android-build-local-$stamp.stderr.log"

Write-Host 'Building Android APK...'
$buildArgs = @(
    "`"$launcher`"",
    'android_build',
    "`"$project`"",
    '--destination',
    "`"$Destination`""
)

$process = Start-Process -FilePath $renpy -ArgumentList $buildArgs -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
if ($process.ExitCode -ne 0) {
    Get-Content -LiteralPath $stdoutLog -ErrorAction SilentlyContinue
    Get-Content -LiteralPath $stderrLog -ErrorAction SilentlyContinue
    throw "Android build failed with exit code $($process.ExitCode)."
}

$apk = Get-ChildItem -Path $Destination -Filter '*.apk' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $apk) {
    throw "Android build completed but no APK was found in $Destination."
}

if (-not $env:MAIL_SUBJECT) {
    $env:MAIL_SUBJECT = "Sam And Em local build ready on git"
}

if (-not $env:MAIL_BODY) {
    $branch = git -C $RepoRoot rev-parse --abbrev-ref HEAD 2>$null
    $commit = git -C $RepoRoot rev-parse --short HEAD 2>$null
    if (-not $branch) { $branch = 'unknown' }
    if (-not $commit) { $commit = 'unknown' }
    $env:MAIL_BODY = @"
A new local Sam And Em Android build is ready.

Repo:
$RepoRoot

Branch:
$branch

Commit:
$commit

The APK was built locally and is ready to push/tag on git.

Logs:
$stdoutLog
$stderrLog
"@
}

python $emailScript

Write-Host "APK ready: $($apk.FullName)"
