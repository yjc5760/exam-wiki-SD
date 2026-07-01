$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding($False)

$qIndexJson = [System.IO.File]::ReadAllText("raw\json\question_index.json", $utf8)
$qIndex = ConvertFrom-Json $qIndexJson

$taxonomyJson = [System.IO.File]::ReadAllText("raw\json\syllabus_taxonomy.json", $utf8)
$taxonomy = ConvertFrom-Json $taxonomyJson

$topicsObj = @{}
$unitsObj = @{}

$sdSubject = $null
foreach ($sub in $taxonomy.subjects) {
    if ($sub.id -eq "SD") {
        $sdSubject = $sub
        break
    }
}

if ($sdSubject -ne $null) {
    foreach ($unit in $sdSubject.units) {
        $uId = $unit.id -replace "^SD-", ""
        $unitsObj[$uId] = $unit.name
        foreach ($topic in $unit.items) {
            $tId = $topic.id -replace "^SD-", ""
            $topicsObj[$tId] = $topic.name
        }
    }
}

$questionsArray = @()
foreach ($q in $qIndex.questions) {
    $modId = $q.moduleId
    $primaryId = ""
    if ($q.primaryTopicId -ne $null) {
        $primaryId = $q.primaryTopicId -replace "^SD-", ""
    }
    
    $sIds = @()
    if ($q.secondaryTopicIds -ne $null) {
        foreach ($s in $q.secondaryTopicIds) {
            $sIds += ($s -replace "^SD-", "")
        }
    }
    
    $designMethod = ""
    if ($q.analysisMethod -ne $null) { 
        $designMethod = $q.analysisMethod 
    } elseif ($q.designMethod -ne $null) {
        $designMethod = $q.designMethod
    }
    
    $tags = @()
    if ($q.tags -ne $null) {
        foreach ($t in $q.tags) { $tags += $t }
    }
    
    $vizList = @()
    $pdfList = @()
    
    $solDir = "raw\solutions\$modId"
    if (Test-Path $solDir) {
        $vizFiles = Get-ChildItem -Path $solDir -Filter "*-viz.html" -File
        foreach ($vf in $vizFiles) {
            $name = $vf.Name
            $prefix = $name -replace "^$modId-", ""
            $prefix = $prefix -replace "-viz\.html$", ""
            $vizList += $prefix
        }
        
        $pdfFiles = Get-ChildItem -Path $solDir -Filter "*.pdf" -File
        foreach ($pf in $pdfFiles) {
            $pdfList += $pf.Name
        }
    }
    
    $qItem = @{
        moduleId = $modId
        primaryId = $primaryId
        sIds = $sIds
        designMethod = $designMethod
        vizList = $vizList
        tags = $tags
        pdfList = $pdfList
    }
    $questionsArray += $qItem
}

$jsContent = "// exam-wiki-SD dashboard data`n`n"

$topicsJson = ConvertTo-Json $topicsObj -Depth 5 -Compress
$topicsJson = [System.Text.RegularExpressions.Regex]::Unescape($topicsJson)
$jsContent += "window.SD_TOPICS = $topicsJson;`n`n"

$unitsJson = ConvertTo-Json $unitsObj -Depth 5 -Compress
$unitsJson = [System.Text.RegularExpressions.Regex]::Unescape($unitsJson)
$jsContent += "window.SD_UNITS = $unitsJson;`n`n"

$jsContent += "window.SD_QUESTIONS = [`n"
$qStrings = @()
foreach ($q in $questionsArray) {
    $sIdsJson = ConvertTo-Json @($q.sIds) -Compress
    if ($sIdsJson -eq $null -or $sIdsJson -eq "null") { $sIdsJson = "[]" }
    
    $vizJson = ConvertTo-Json @($q.vizList) -Compress
    if ($vizJson -eq $null -or $vizJson -eq "null") { $vizJson = "[]" }
    
    $tagsJson = ConvertTo-Json @($q.tags) -Compress
    if ($tagsJson -eq $null -or $tagsJson -eq "null") { $tagsJson = "[]" }
    
    $pdfJson = ConvertTo-Json @($q.pdfList) -Compress
    if ($pdfJson -eq $null -or $pdfJson -eq "null") { $pdfJson = "[]" }
    
    $modIdJson = ConvertTo-Json $q.moduleId
    $primaryIdJson = ConvertTo-Json $q.primaryId
    $designJson = ConvertTo-Json $q.designMethod
    
    $qStr = "  [$modIdJson, $primaryIdJson, $sIdsJson, $designJson, $vizJson, $tagsJson, $pdfJson]"
    $qStr = [System.Text.RegularExpressions.Regex]::Unescape($qStr)
    $qStrings += $qStr
}
$jsContent += ($qStrings -join ",`n")
$jsContent += "`n];`n"

[System.IO.File]::WriteAllText("dashboard-data.js", $jsContent, $utf8)

$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logEntry = "- $date [REFRESH-DASHBOARD] Updated dashboard-data.js`n"
if (Test-Path "wiki\log.md") {
    $logContent = [System.IO.File]::ReadAllText("wiki\log.md", $utf8)
    $logContent += $logEntry
    [System.IO.File]::WriteAllText("wiki\log.md", $logContent, $utf8)
}

Write-Host "Dashboard data refreshed."
