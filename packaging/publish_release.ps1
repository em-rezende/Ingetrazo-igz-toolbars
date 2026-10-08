<#
.SYNOPSIS
    Creates the GitHub Release for a tag, attaches the toolbar archive and
    verifies the uploaded sha256.

.DESCRIPTION
    Automation for step 4 of PUBLISHING.md. It

      1. checks that dist/igz_tb_toolbar.zip hashes to the sha256 advertised in
         ingetrazo-extensions-submission/extensions/igz_toolbars.toml;
      2. reuses the GitHub token already stored by Git Credential Manager (the
         same one `git push` uses) - the value is captured into a variable and
         never printed;
      3. creates the release for -Tag, or reuses the one already there (a re-run
         with the same notes and the same archive changes nothing), and uploads
         the archive as igz_tb_toolbar.zip;
      4. re-reads the release through the API and confirms that the asset size
         and the `digest` (sha256) GitHub reports match the local archive.

    Run it after steps 2 and 3 of PUBLISHING.md (code pushed, tag pushed).

.PARAMETER Tag
    Release tag, e.g. v1.5.2. The tag must already exist on the remote.

.PARAMETER Notes
    Markdown file with the release body (same style as previous releases).
    Defaults to packaging\release_notes\<Tag>.md, e.g. the body of v1.5.2 in
    packaging\release_notes\v1.5.2.md.

.PARAMETER ExpectedSha256
    sha256 the uploaded asset must have. Defaults to the value in the catalog
    entry (ingetrazo-extensions-submission/extensions/igz_toolbars.toml).

.PARAMETER DryRun
    Performs the read-only checks only (archive hash, credential, existing
    release and asset) and prints what would happen. Nothing is created,
    uploaded or deleted.

.PARAMETER Force
    Uploads the archive even when the release already carries an asset with the
    expected sha256. Without it, re-running for a published tag leaves both the
    release text and the asset untouched.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File packaging\publish_release.ps1 -Tag v1.5.2

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File packaging\publish_release.ps1 -Tag v1.5.2 -DryRun

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File packaging\publish_release.ps1 -Tag v1.5.2 -Notes packaging\release_notes\v1.5.2.md -Force
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Tag,
    [string]$Notes,
    [string]$ExpectedSha256,
    [string]$Repo = 'em-rezende/Ingetrazo-igz-toolbars',
    [string]$AssetName = 'igz_tb_toolbar.zip',
    [string]$Zip,
    [string]$ReleaseName,
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$script:lastCode = 0
$script:lastBody = ''

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $Zip) { $Zip = Join-Path $repoRoot 'dist\igz_tb_toolbar.zip' }
if (-not $ReleaseName) { $ReleaseName = 'igz_toolbars ' + ($Tag -replace '^v', '') }
if (-not $Notes) {
    $Notes = Join-Path $PSScriptRoot "release_notes\$Tag.md"
    if (-not (Test-Path $Notes)) { throw "-Notes was not given and $Notes does not exist" }
}
if (-not $ExpectedSha256) {
    $entry = Join-Path $repoRoot 'ingetrazo-extensions-submission\extensions\igz_toolbars.toml'
    if (Test-Path $entry) {
        $m = [regex]::Match((Get-Content -Raw -Encoding UTF8 $entry), '(?m)^sha256\s*=\s*"([0-9a-fA-F]{64})"')
        if ($m.Success) { $ExpectedSha256 = $m.Groups[1].Value.ToLower() }
    }
}

# 1. the archive we are about to publish
if (-not (Test-Path $Zip)) { throw "missing archive: $Zip" }
if (-not (Test-Path $Notes)) { throw "missing release notes: $Notes" }
$localHash = (Get-FileHash -Algorithm SHA256 $Zip).Hash.ToLower()
Write-Host "archive  $Zip"
Write-Host "         $((Get-Item $Zip).Length) bytes, sha256 $localHash"
if ($ExpectedSha256) {
    if ($localHash -ne $ExpectedSha256) {
        throw "local sha256 $localHash != expected $ExpectedSha256 (rebuild the archive or fix the catalog entry)"
    }
    Write-Host 'OK local archive matches the catalog sha256'
} else {
    Write-Warning "no sha256 to compare against; the catalog entry must advertise $localHash"
}

# 2. token from the credential Git Credential Manager stored for github.com
$env:GIT_TERMINAL_PROMPT = '0'
$fill = "protocol=https`nhost=github.com`n`n" | git credential fill 2>$null
$token = (($fill | Where-Object { $_ -like 'password=*' }) -replace '^password=', '').Trim()
if (-not $token) { throw 'no stored credential for github.com (run `git push` once to store one)' }
Write-Host "OK credential found, length $($token.Length) (value hidden)"

$hdr = @{
    Authorization          = "Bearer $token"
    Accept                 = 'application/vnd.github+json'
    'User-Agent'           = 'igz-publish-release'
    'X-GitHub-Api-Version' = '2022-11-28'
}
$api = "https://api.github.com/repos/$Repo"

function Invoke-Api {
    param([string]$Uri, [string]$Method = 'Get', $Body = $null, [string]$ContentType = $null)
    try {
        if ($Body) {
            $r = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $hdr -Body $Body -ContentType $ContentType
        } else {
            $r = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $hdr
        }
        $script:lastCode = 200
        $script:lastBody = ''
        return $r
    } catch {
        $resp = $_.Exception.Response
        if ($resp) {
            $script:lastCode = [int]$resp.StatusCode
            $script:lastBody = (New-Object System.IO.StreamReader($resp.GetResponseStream())).ReadToEnd()
            Write-Host "!! HTTP $script:lastCode on $Method $Uri"
            Write-Host "   $($script:lastBody)"
        } else {
            $script:lastCode = -1
            $script:lastBody = $_.Exception.Message
            Write-Host "!! transport error on $Method ${Uri}: $($_.Exception.Message)"
        }
        return $null
    }
}
# 3. who this token belongs to and what it is allowed to do
try {
    $me = Invoke-WebRequest -Uri 'https://api.github.com/user' -Headers $hdr -UseBasicParsing
    Write-Host "OK token belongs to $((ConvertFrom-Json $me.Content).login)"
    Write-Host "   scopes [$($me.Headers['x-oauth-scopes'])]"
} catch {
    Write-Host "!! GET /user failed: $($_.Exception.Message)"
}
$repoInfo = Invoke-Api -Uri $api
if ($repoInfo) {
    Write-Host "OK repository reachable, permissions $($repoInfo.permissions | ConvertTo-Json -Compress)"
} else {
    Write-Host "!! repository not reachable (HTTP $script:lastCode)"
}

# 4. release body (read as UTF-8 so accented text survives; BOM stripped)
$notes = (Get-Content -Raw -Encoding UTF8 $Notes) -replace "^\uFEFF", ''

if ($DryRun) {
    Write-Host '--- dry run: read-only checks only ---'
    $known = Invoke-Api -Uri "$api/releases/tags/$Tag"
    if ($known) {
        Write-Host "existing release $($known.id): $($known.name) (draft $($known.draft))"
        $assets = @(Invoke-Api -Uri "$api/releases/$($known.id)/assets")
        if ($assets.Count -eq 0) { Write-Host '  no asset yet: the archive would be uploaded' }
        foreach ($a in $assets) {
            $note = if (('sha256:' + $localHash) -eq $a.digest) { 'identical to the local archive' } else { 'would be replaced' }
            Write-Host "  asset $($a.name): $($a.size) bytes, digest $($a.digest) - $note"
        }
    } else {
        Write-Host "no release for $Tag yet (HTTP $script:lastCode): it would be created as '$ReleaseName'"
    }
    Write-Host 'dry run finished - nothing was created, uploaded or deleted'
    return
}

# 5. create the release, or reuse the one already published for that tag
$payload = @{ tag_name = $Tag; name = $ReleaseName; body = $notes; draft = $false; prerelease = $false }
$body = [System.Text.Encoding]::UTF8.GetBytes(($payload | ConvertTo-Json -Depth 3))
$rel = Invoke-Api -Uri "$api/releases" -Method Post -Body $body -ContentType 'application/json; charset=utf-8'
$created = [bool]$rel
if (-not $rel) {
    Write-Host "POST /releases answered HTTP $script:lastCode; reusing the release already published for $Tag"
    $rel = Invoke-Api -Uri "$api/releases/tags/$Tag"
}
if (-not $rel) { throw "no release created or found for $Tag (last HTTP $script:lastCode)" }
Write-Host "OK release $($rel.id) $(if ($created) { 'created' } else { 'reused' }): $($rel.name) (draft $($rel.draft))"
Write-Host "   $($rel.html_url)"

# the published text is refreshed only when it really differs, so a re-run is a no-op
if (-not $created) {
    $live = ($rel.body -replace "`r`n", "`n").TrimEnd()
    $wanted = ($notes -replace "`r`n", "`n").TrimEnd()
    if ($live -eq $wanted) {
        Write-Host 'OK release notes are already identical to the notes file; left untouched'
    } else {
        $patch = [System.Text.Encoding]::UTF8.GetBytes((@{ name = $ReleaseName; body = $notes } | ConvertTo-Json -Depth 2))
        $patched = Invoke-Api -Uri "$api/releases/$($rel.id)" -Method Patch -Body $patch -ContentType 'application/json; charset=utf-8'
        if ($patched) {
            $rel = $patched
            Write-Host 'OK release notes refreshed from the notes file'
        } else {
            Write-Host "!! could not refresh the release notes (HTTP $script:lastCode)"
        }
    }
}

# 6. drop a stale asset with the same name, then upload the archive
$upload = $rel.upload_url -replace '\{\?.*$', ''
$current = @(Invoke-Api -Uri "$api/releases/$($rel.id)/assets") | Where-Object { $_.name -eq $AssetName } | Select-Object -First 1
$needUpload = $true
if ($current -and $current.digest -eq "sha256:$localHash" -and -not $Force) {
    $needUpload = $false
    Write-Host "OK $AssetName is already published with this sha256 (asset $($current.id), $($current.size) bytes); nothing to upload"
    Write-Host '   (pass -Force to upload it again anyway)'
}
if ($needUpload) {
    if ($current) {
        $null = Invoke-Api -Uri "$api/releases/assets/$($current.id)" -Method Delete
        Write-Host "OK removed the previous $AssetName (asset $($current.id))"
    }
    try {
        $up = Invoke-WebRequest -Uri "$upload`?name=$AssetName" -Method Post -Headers $hdr -InFile $Zip -ContentType 'application/zip' -UseBasicParsing
        Write-Host "OK uploaded $AssetName (HTTP $($up.StatusCode))"
    } catch {
        $resp = $_.Exception.Response
        if ($resp) {
            $detail = (New-Object System.IO.StreamReader($resp.GetResponseStream())).ReadToEnd()
            Write-Host "!! upload failed: HTTP $([int]$resp.StatusCode) $detail"
        } else {
            Write-Host "!! upload failed: $($_.Exception.Message)"
        }
        throw
    }
}

# 7. confirm what the public download URL now serves
$rel2 = Invoke-Api -Uri "$api/releases/tags/$Tag"
$asset = @($rel2.assets) | Where-Object { $_.name -eq $AssetName } | Select-Object -First 1
if (-not $asset) { throw "the release has no asset named $AssetName" }
Write-Host "   asset $($asset.size) bytes (local $((Get-Item $Zip).Length))"
Write-Host "   $($asset.browser_download_url)"
if ($asset.digest -eq "sha256:$localHash") {
    Write-Host 'VERIFIED remote digest == local sha256'
} else {
    Write-Host "   digest reported by GitHub: $($asset.digest)"
    $tmp = Join-Path $env:TEMP 'igz_asset_check.zip'
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp -UseBasicParsing
    $downHash = (Get-FileHash -Algorithm SHA256 $tmp).Hash.ToLower()
    Remove-Item $tmp -Force
    if ($downHash -ne $localHash) { throw "downloaded sha256 $downHash != $localHash" }
    Write-Host 'VERIFIED downloaded asset == local sha256'
}
Write-Host "DONE release $Tag published at $($rel2.published_at)"
