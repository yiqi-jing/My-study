# MySQL 8.4.9 Auto Install Script
# Run as Administrator!

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] Please run as Administrator!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MySQL 8.4.9 Auto Install Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$mysqlBaseDir = "F:\MySQL"
$mysqlInstallDir = "F:\MySQL\MySQL Server 8.4"
$mysqlDataDir = "F:\MySQL\data"
$mysqlTempDir = "F:\MySQL\temp"
$mysqlPort = 3306
$rootPassword = "021219Hjk!"
$serviceName = "MySQL84"

# Step 1: Check winget
Write-Host "[1/7] Checking winget..." -ForegroundColor Green
$wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
if (-not $wingetCmd) {
    Write-Host "[ERROR] winget not found" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  winget found" -ForegroundColor Gray

# Step 2: Install MySQL via winget
Write-Host "[2/7] Installing MySQL 8.4.9 (may take a few minutes)..." -ForegroundColor Green
$installed = Get-Package -Name "*MySQL Server*" -ErrorAction SilentlyContinue
if ($installed) {
    Write-Host "  MySQL already installed: $($installed.Version)" -ForegroundColor Yellow
} else {
    winget install Oracle.MySQL --version 8.4.9 --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] MySQL install failed" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "  MySQL 8.4.9 installed" -ForegroundColor Gray
}

# Step 3: Move MySQL to F drive
Write-Host "[3/7] Moving MySQL to F drive..." -ForegroundColor Green
$sourceDir = $null
$possiblePaths = @(
    "C:\Program Files\MySQL\MySQL Server 8.4",
    "C:\Program Files (x86)\MySQL\MySQL Server 8.4"
)
foreach ($p in $possiblePaths) {
    if (Test-Path "$p\bin\mysqld.exe") {
        $sourceDir = $p
        break
    }
}

if (-not $sourceDir) {
    Write-Host "[ERROR] Cannot find MySQL install dir" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  Found MySQL at: $sourceDir" -ForegroundColor Gray

if ($sourceDir -ne $mysqlInstallDir) {
    if (Test-Path $mysqlInstallDir) {
        Write-Host "  F drive already has MySQL dir, skip copy" -ForegroundColor Yellow
    } else {
        Write-Host "  Copying to F drive (may take a few minutes)..." -ForegroundColor Yellow
        Copy-Item -Path $sourceDir -Destination $mysqlInstallDir -Recurse -Force
        Write-Host "  Copy done" -ForegroundColor Gray
    }

    Write-Host "  Uninstalling C drive MySQL package..." -ForegroundColor Yellow
    $wmi = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like '*MySQL Server*' }
    if ($wmi) {
        $wmi.Uninstall() | Out-Null
        Write-Host "  Uninstalled" -ForegroundColor Gray
    }

    if (Test-Path "C:\Program Files\MySQL") {
        Remove-Item -Path "C:\Program Files\MySQL" -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path "C:\Program Files (x86)\MySQL") {
        Remove-Item -Path "C:\Program Files (x86)\MySQL" -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  C drive MySQL files cleaned" -ForegroundColor Gray
} else {
    Write-Host "  MySQL already on F drive, skip" -ForegroundColor Gray
}

if (-not (Test-Path "$mysqlInstallDir\bin\mysqld.exe")) {
    Write-Host "[ERROR] mysqld.exe not found at $mysqlInstallDir\bin" -ForegroundColor Red
    pause
    exit 1
}

# Step 4: Create directories
Write-Host "[4/7] Creating data and temp directories..." -ForegroundColor Green
New-Item -ItemType Directory -Path $mysqlDataDir -Force | Out-Null
New-Item -ItemType Directory -Path $mysqlTempDir -Force | Out-Null
Write-Host "  Data dir: $mysqlDataDir" -ForegroundColor Gray
Write-Host "  Temp dir: $mysqlTempDir" -ForegroundColor Gray

# Step 5: Create my.ini
Write-Host "[5/7] Creating my.ini config file..." -ForegroundColor Green
$basedirEsc = $mysqlInstallDir -replace '\\', '\\'
$datadirEsc = $mysqlDataDir -replace '\\', '\\'
$tmpdirEsc = $mysqlTempDir -replace '\\', '\\'

$iniLines = @(
    "[mysqld]",
    "port=$mysqlPort",
    "basedir=$basedirEsc",
    "datadir=$datadirEsc",
    "tmpdir=$tmpdirEsc",
    "max_connections=200",
    "max_connect_errors=10",
    "character-set-server=utf8mb4",
    "default-storage-engine=INNODB",
    "mysql_native_password=ON",
    "",
    "[mysql]",
    "default-character-set=utf8mb4",
    "",
    "[client]",
    "port=$mysqlPort",
    "default-character-set=utf8mb4"
)
$iniPath = "$mysqlInstallDir\my.ini"
[System.IO.File]::WriteAllLines($iniPath, $iniLines, (New-Object System.Text.UTF8Encoding $false))
Write-Host "  Config file: $iniPath" -ForegroundColor Gray

# Step 6: Initialize database
Write-Host "[6/7] Initializing MySQL database..." -ForegroundColor Green
$dataFiles = Get-ChildItem $mysqlDataDir -ErrorAction SilentlyContinue
if ($dataFiles.Count -gt 0) {
    Write-Host "  Data dir has data, skip init" -ForegroundColor Yellow
} else {
    $initArgs = @("--defaults-file=`"$iniPath`"", "--initialize-insecure", "--console")
    $initProc = Start-Process -FilePath "$mysqlInstallDir\bin\mysqld.exe" -ArgumentList $initArgs -NoNewWindow -Wait -PassThru
    if ($initProc.ExitCode -ne 0) {
        Write-Host "[ERROR] MySQL init failed" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "  Init done" -ForegroundColor Gray
}

# Step 7: Install and start service
Write-Host "[7/7] Installing and starting MySQL service..." -ForegroundColor Green

$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "  Found existing service, removing..." -ForegroundColor Yellow
    Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    & "$mysqlInstallDir\bin\mysqld.exe" --remove $serviceName
    Start-Sleep -Seconds 2
}

$installArgs = @("--install", $serviceName, "--defaults-file=`"$iniPath`"")
$installProc = Start-Process -FilePath "$mysqlInstallDir\bin\mysqld.exe" -ArgumentList $installArgs -NoNewWindow -Wait -PassThru

if ($installProc.ExitCode -ne 0) {
    Write-Host "[ERROR] Service install failed" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  Service installed: $serviceName" -ForegroundColor Gray

Start-Service -Name $serviceName
Start-Sleep -Seconds 3

$svc = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($svc.Status -eq 'Running') {
    Write-Host "  Service started successfully!" -ForegroundColor Gray
} else {
    Write-Host "[WARN] Service status: $($svc.Status)" -ForegroundColor Yellow
}

# Set root password
Write-Host ""
Write-Host "Setting root password..." -ForegroundColor Green
$sql = "ALTER USER 'root'@'localhost' IDENTIFIED BY '$rootPassword'; FLUSH PRIVILEGES;"
& "$mysqlInstallDir\bin\mysql.exe" -u root -e $sql 2>&1 | Out-Null
Write-Host "  Root password set" -ForegroundColor Gray

# Verify connection
Write-Host ""
Write-Host "Verifying connection..." -ForegroundColor Green
& "$mysqlInstallDir\bin\mysql.exe" -u root -p"$rootPassword" -e "SELECT VERSION(); SHOW DATABASES;" 2>&1

# Add to PATH
Write-Host ""
Write-Host "Adding to system PATH..." -ForegroundColor Green
$binPath = "$mysqlInstallDir\bin"
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
if ($currentPath -notlike "*$binPath*") {
    [Environment]::SetEnvironmentVariable('Path', "$currentPath;$binPath", 'Machine')
    Write-Host "  Added $binPath to system PATH" -ForegroundColor Gray
} else {
    Write-Host "  PATH already contains MySQL bin" -ForegroundColor Gray
}

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MySQL Install Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Version:    MySQL 8.4.9" -ForegroundColor White
Write-Host "  Port:       $mysqlPort" -ForegroundColor White
Write-Host "  Username:   root" -ForegroundColor White
Write-Host "  Password:   $rootPassword" -ForegroundColor White
Write-Host "  Install:    $mysqlInstallDir" -ForegroundColor White
Write-Host "  Data:       $mysqlDataDir" -ForegroundColor White
Write-Host "  Service:    $serviceName" -ForegroundColor White
Write-Host "  Config:     $iniPath" -ForegroundColor White
Write-Host ""
Write-Host "  Connect:    mysql -u root -p`"$rootPassword`"" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Service control:" -ForegroundColor Yellow
Write-Host "    Start: net start $serviceName" -ForegroundColor Gray
Write-Host "    Stop:  net stop $serviceName" -ForegroundColor Gray
Write-Host ""
pause
