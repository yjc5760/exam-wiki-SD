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
    
    $qItem = @{
        moduleId = $modId
        primaryId = $primaryId
        sIds = $sIds
        designMethod = $designMethod
        tags = $tags
    }
    $questionsArray += $qItem
}

$jsContent = "// exam-wiki-SD 儀表板資料檔`n"
$jsContent += "// 由 question_index.json 與 syllabus_taxonomy.json 生成。索引或命題大綱更新後，對 Cowork 說「更新儀表板資料」即可重新生成。`n"
$jsContent += "// 註：window.SD_TOPICS 與 window.SD_UNITS 皆由 REFRESH-DASHBOARD 指令動態由 syllabus_taxonomy.json 擷取。`n"
$jsContent += "// 格式：[moduleId, primaryTopicId(縮寫), secondaryTopicIds, designMethod, tags]（2026-11-01 起移除 viz 與 pdf 補充筆記欄）`n`n"

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
    
    $tagsJson = ConvertTo-Json @($q.tags) -Compress
    if ($tagsJson -eq $null -or $tagsJson -eq "null") { $tagsJson = "[]" }
    
    $modIdJson = ConvertTo-Json $q.moduleId
    $primaryIdJson = ConvertTo-Json $q.primaryId
    $designJson = ConvertTo-Json $q.designMethod
    
    $qStr = "  [$modIdJson, $primaryIdJson, $sIdsJson, $designJson, $tagsJson]"
    $qStr = [System.Text.RegularExpressions.Regex]::Unescape($qStr)
    $qStrings += $qStr
}
$jsContent += ($qStrings -join ",`n")
$jsContent += "`n];`n"

[System.IO.File]::WriteAllText("dashboard-data.js", $jsContent, $utf8)

$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logEntry = "- $date [REFRESH-DASHBOARD] Updated dashboard-data.js`n"
if (Test-Path "wiki\queries\log.md") {
    $logContent = [System.IO.File]::ReadAllText("wiki\queries\log.md", $utf8)
    $logContent += $logEntry
    [System.IO.File]::WriteAllText("wiki\queries\log.md", $logContent, $utf8)
}

Write-Host "Dashboard data refreshed."
