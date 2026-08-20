# Wiki 操作紀錄

> append-only，請勿刪除已有紀錄

---

## 2026-05-29

- **[INIT]** 從 exam-wiki-SS 克隆，全面改寫為 RC 科目（鋼筋混凝土設計與預力）
  - 改寫 CLAUDE.md（身份層）、CLAUDE-SOLVE.md（解題規範）、CLAUDE-SPEC.md（命名規格）
  - 改寫 CLAUDE-CODE.md（Runbook）、README.md（導覽）
  - 重建 wiki/index.md（RC 七層架構）、wiki/by-year.md（2002–2025 空白表格）
  - 重建 raw/json/question_index.json（空白索引）、concepts.json（RC 核心概念）
  - 科目代碼：RC｜題目編號格式：RC-YYYY-N

## 2026-06-07

- **[INGEST-BATCH]** 批次 ingest 94 題（所有 verificationStatus=verified 且 hasSolution=true）
  - 生成 wiki/problems/ 共 94 個頁面
  - 重建 wiki/index.md（依 RC-UN-n 分類，含題目連結表格）
  - 重建 wiki/by-year.md（2002–2025 年，含題號連結）
  - 涵蓋年份：2002–2025

## 2026-06-07

- **[COMPILE-ALL]** 完整重新編譯 wiki 知識庫
  - 生成 wiki/concepts/：10 個概念頁面
  - 生成 wiki/methods/：4 個解題方法論頁面
  - 確認 wiki/queries/ 存在
  - 建立 wiki/philosophy/index.md
  - wiki/problems/（94題）已於本日批次 ingest 完成
  - 未覆蓋：diagnosis/ · failure-modes/ · materials/ · code-ref/（Cowork 直接維護）

## 2026-06-07

- **[LINT-FIX]** 修復全部 7 項 lint 問題：
  - 概念頁補充：DUCTILE-FAILURE, LONG-COLUMN-MOMENT-MAGNIFIER, LONG-TERM-DEFLECTION, CREEP-SHRINKAGE, SPECIAL-MOMENT-FRAME-BEAM, SPECIAL-MOMENT-FRAME-COLUMN（6 頁）
  - 圖說補充：RC-2024-4-fig-1、RC-2025-3-fig-1（圖說缺漏）；RC-2023-4 加入 eqn-1.png 引用與 LaTeX 圖說
  - diagnosis/ 建立：beam-flexure, column-pm, shear-torsion, prestress, deflection-crack（5 頁）
  - failure-modes/ 建立：flexure, shear, crushing, deflection, cracking（5 頁）
  - materials/ 建立：concrete-stress-strain, steel-yielding, creep-shrinkage, prestress-strand（4 頁）
  - P-M 互動圖生成：10 個柱設計題（RC-2002-2 等），更新 hasViz=true

## 2026-06-07

- **[CLEANUP]** 清除 SS 鋼結構殘留：186 個檔案（problems/98 + concepts/58 + methods/19 + traps/11）
- **[CONCEPTS]** concepts.json 新增 7 個高頻概念（SHEAR-STRENGTH、TORSION-DESIGN、PUNCHING-SHEAR、SEISMIC-DESIGN、DEVELOPMENT-LENGTH、DEFLECTION-CONTROL、CRACK-WIDTH）
- **[FIX]** RC-2012-2 verificationStatus 改回 unverified（hasSolution=false，狀態矛盾修正）
- **[QUERY]** 建立 wiki/queries/題庫缺口報告（2017整年缺失、RC-2016-3、RC-2012-2）

## 2026-06-07

- **[REINDEX+INGEST]** 題庫補齊，新增 6 題（RC-2012-2、RC-2016-3、RC-2017-1~4）
  - question_index.json：共 100 題（verified+hasSolution：100 題）
  - wiki/problems/：新增 6 個頁面
  - wiki/by-year.md、wiki/index.md：重建完成
  - 題庫缺口報告更新：無缺口

## 2026-06-07

- **[CLEANUP-2]** 清除 SS 殘留 56 個（code-ref/22、philosophy/10、diagnosis/8、failure-modes/5、materials/5、queries/6）
- **[REBUILD]** 重建各目錄 RC 版 index.md（6 個目錄）
- **[ADD]** 補建 wiki/diagnosis/seismic.md

## 2026-06-08

- **[COMPILE-ALL]** 全面重建 wiki 知識庫（compile-all + ingest 完整驗證）
  - 確認 wiki/concepts/：17 個概念頁面（BALANCED-REINFORCEMENT-RATIO 至 CRACK-WIDTH 全部存在）
  - 確認 wiki/problems/：100 個題目頁面（2002–2025 全部 verified 題目）
  - 重建 wiki/index.md：採七層知識架構 + 四單元分類導航格式，含全部 100 題連結
  - 確認 wiki/by-year.md：2002–2025 完整年份表格（無需修改）
  - **[NEW]** 建立 wiki/traps/：13 個陷阱頁面 + index.md（T形梁、φ值、耐震Ve、預力fps、預力損失、扭力門檻、衝剪、細長柱、平衡鋼筋比、雙筋梁壓力筋、梁柱接頭、剪力臨界斷面、有效慣性矩）
  - **[LINT]** 執行 16 項健檢，結果：11項PASS、2項WARNING、3項SKIP（需bash）；完整報告：wiki/queries/lint-report-2026-06-08.md
  - **[FIX-1]** 同步 STIRRUP-DESIGN 至 concepts.json（第 18 個概念）
  - **[FIX-2]** 建立 wiki/code-ref/ 實體頁面（ACI-318.md、CNS-1480.md、seismic-code.md），更新 index.md；code-ref 從 stub 升格為完整規範速查層
  - 操作者：Cowork

## 2026-06-09

- **[COMPILE-ALL]** 全面重建 wiki 知識庫（全部修正），compile-all 第二次完整執行
  - 全部 100 題 wiki/problems/ 頁面確認（2002–2025 年，100 題均 verified）
  - **[CONCEPTS]** 24 個概念頁面全部以 §7.2 完整格式重新生成：
    - BALANCED-REINFORCEMENT-RATIO、WHITNEY-STRESS-BLOCK、BETA1-FACTOR
    - PM-INTERACTION-DIAGRAM、BALANCED-POINT、EFFECTIVE-MOMENT-OF-INERTIA
    - CRACKING-MOMENT、PRESTRESS-LOSS、EFFECTIVE-PRESTRESS、STRONG-COLUMN-WEAK-BEAM
    - SHEAR-STRENGTH、TORSION-DESIGN、PUNCHING-SHEAR、SEISMIC-DESIGN
    - DEVELOPMENT-LENGTH、DEFLECTION-CONTROL、CRACK-WIDTH、STIRRUP-DESIGN
    - DUCTILE-FAILURE、LONG-COLUMN-MOMENT-MAGNIFIER、LONG-TERM-DEFLECTION
    - CREEP-SHRINKAGE、SPECIAL-MOMENT-FRAME-BEAM、SPECIAL-MOMENT-FRAME-COLUMN
  - 格式特徵：每頁含完整 LaTeX 公式（$$...$$）、定義段落、前置概念、相關概念、常見陷阱、出現題目表格
  - **[INDEX]** 重建 wiki/index.md：七層知識架構表 + 24 概念快速導覽表（依四單元分類）+ 全 100 題連結
  - **[BY-YEAR]** 重建 wiki/by-year.md：2002–2025 年全 100 題，改為 [[RC-YYYY-N]] Obsidian 連結格式
  - 操作者：Cowork

## 2026-06-09

- **[METHODS]** 建立 wiki/methods/ 完整解題方法論目錄（Layer 3）
  - 新建 index.md：列出 8 個方法論頁面
  - 新建 WHITNEY-STRESS-BLOCK-METHOD.md（等值矩形應力塊，RC-U1-1/U1-2）
  - 升級 PM-INTERACTION-DIAGRAM.md（原 stub → 完整版含 LaTeX 公式與出現題目表）
  - 新建 MOMENT-MAGNIFIER.md（長柱放大彎矩法，RC-U1-3）
  - 新建 EFFECTIVE-INERTIA.md（有效慣性矩撓度計算法，RC-U3-1）
  - 新建 PRESTRESS-LOSS-CALC.md（預力損失計算流程，RC-U4-3）
  - 新建 T-BEAM-ANALYSIS.md（T 形梁彎矩強度分析法，RC-U1-1）
  - 新建 FRICTION-LOSS-METHOD.md（摩擦損失計算法，RC-U4-3）
  - 新建 SEISMIC-CAPACITY-METHOD.md（耐震能力設計法，RC-U3-3）
  - 知識庫健康狀態：wiki/ 七層架構全部完整，無缺漏
  - 操作者：Cowork

## 2026-06-10

- **[FREQUENCY]** 執行 frequency 指令，生成 wiki/queries/frequency-20260610.md
  - 統計全 100 題（2002–2025）各 topicId 出現頻次（primary + secondary）
  - 結果：RC-U1-1=22、RC-U4-1=21、RC-U1-2=19、RC-U3-3=16、RC-U2-1=16
  - 操作者：Cowork

- **[PREDICT]** 執行 predict 指令，生成 wiki/queries/predict-2026-20260610.md
  - 基於頻次統計＋近年趨勢＋補考點分析推測 2026 高機率考題
  - 優先補考點：RC-U3-1（8 年未考）、RC-U4-3（7 年未考）、RC-U1-3（10 年未考）
  - 操作者：Cowork

- **[RAW-METHODS]** 補建 raw/solutions/methods/ 來源檔案（4 個方法論 .md）
  - 新建 raw/solutions/methods/effective-inertia-deflection/effective-inertia-deflection.md
  - 新建 raw/solutions/methods/moment-magnifier-method/moment-magnifier-method.md
  - 新建 raw/solutions/methods/prestress-loss-calculation/prestress-loss-calculation.md
  - 新建 raw/solutions/methods/pm-interaction-diagram/pm-interaction-diagram.md
  - 修正 raw/→wiki/ 單向資料流缺口，4 個 wiki/methods/ 頁面現有對應原始檔
  - 操作者：Cowork

- **[TRAPS-BACKLINKS]** 建立 traps↔problems 雙向連結
  - 讀取全部 13 個 wiki/traps/ 陷阱頁，建立完整 trap→problem 對應表
  - 在 52 個 wiki/problems/ 頁末尾加入「## 相關陷阱」反向連結區塊
  - 涵蓋陷阱：T-BEAM-EFFECTIVE-WIDTH、BALANCED-RATIO-BOUNDARY、PHI-FACTOR-TRANSITION、COMPRESSION-STEEL-YIELDING、SHEAR-CRITICAL-SECTION、TORSION-THRESHOLD、DEFLECTION-EFFECTIVE-INERTIA、PUNCHING-SHEAR-CRITICAL、SEISMIC-BEAM-VE、JOINT-SHEAR-EFFECTIVE-AREA、LONG-COLUMN-SLENDERNESS、PRESTRESS-LOSS-SEQUENCE、PRESTRESS-FPS-FORMULA
  - wiki/traps/ 雙向連結完整度：13/13 陷阱頁均建立反向連結
  - 操作者：Cowork

## 2026-06-11

- **[HEALTH-CHECK]** 知識庫一致性健檢（補完 2026-06-08 lint 報告的 4 項 SKIP 掃描）
  - hasViz 比對：索引 14 題 hasViz=true ↔ raw/solutions/ 實際 16 個 *-viz.html（RC-2014-2、RC-2014-4 各 2 個），完全一致 ✅
  - hasHandwritten 比對：索引 0 題 ↔ 實際 0 個 *hand*.png，一致 ✅
  - 圖說掃描：59 個含 fig-*.png 的解析檔全部具備「圖說：」段落 ✅
  - lint 待補清單覆核：code-ref 實體頁 ✅、STIRRUP-DESIGN 已入 concepts.json ✅、raw methods 來源 ✅（均已於 06-08~06-10 解決）
  - 結論：資料層無待修項
  - 操作者：Cowork

- **[DASHBOARD]** 建立知識庫儀表板（新增使用者入口）
  - 新建 dashboard.html（離線單檔，雙擊即用）：題庫瀏覽（年份/單元/考點/設計法/標籤/關鍵字篩選）、考點統計圖、近5年走向、高頻標籤、讀書進度追蹤（localStorage）、七層架構導覽、16 指令速查
  - 新建 dashboard-data.js（question_index.json 快照，100 題）
  - 新增指令 REFRESH-DASHBOARD（觸發語句「更新儀表板資料」），登錄於 CLAUDE-CODE.md
  - 操作者：Cowork

- **[DASHBOARD-v2]** 儀表板新增站內解析閱讀器
  - 「完整解析」改於站內彈窗開啟：內建 Markdown 渲染器（標題/表格/清單/引用/程式碼區塊/圖片）＋ KaTeX 公式渲染（$...$ 與 $$...$$，CDN 載入、離線時顯示原始 LaTeX）
  - 因瀏覽器 file:// 安全限制，採 File System Access API：首次使用授權選擇 exam-wiki-RC 資料夾一次（儲存於 IndexedDB），即可讀取所有解析檔與附圖
  - 題目附圖以 Blob URL 載入；解析內 .md 相對連結可於閱讀器內跳轉
  - 移除題卡「wiki 題目頁」連結（依使用者要求）；知識庫導覽卡片也改走站內閱讀器
  - 操作者：Cowork

- **[DASHBOARD-v3]** 解析閱讀器新增「匯出 PDF」按鈕
  - 採瀏覽器原生列印管道（目的地選「另存為 PDF」）：向量文字、中文與 KaTeX 公式完整保留、離線可用
  - 列印樣式僅輸出解析內容＋標頭（題號、來源路徑、匯出日期）；表格/圖片/公式避免跨頁截斷
  - 匯出時自動以題號設定預設 PDF 檔名
  - 操作者：Cowork

- **[METHODS-CONSOLIDATION]** 整併 wiki/methods/ 雙命名體系（lint 後續優化）
  - 問題：methods/ 同時存在大寫頁（8 個，06-09 建立、index 引用、無 raw 來源）與 kebab 頁（3 個，06-10 raw 對應版），4 組內容重複；且多數大寫頁「出現題目」表與 question_index 不符（如 EFFECTIVE-INERTIA 原列 4 題中 3 題為剪力牆/預力/扭力題）
  - 整併為 8 個 kebab-case 方法頁（符合 CLAUDE-SPEC 命名規範）：whitney-stress-block-method、pm-interaction-diagram、moment-magnifier-method、t-beam-analysis、effective-inertia-deflection、seismic-capacity-method、prestress-loss-calculation、friction-loss-method
  - 所有「出現題目」表依 question_index.json 標籤重新核實重建
  - 補建 4 個 raw 來源：whitney-stress-block-method、t-beam-analysis、friction-loss-method、seismic-capacity-method；更新既有 4 個 raw 來源為完整版（與 wiki 頁同步）
  - 重寫 wiki/methods/index.md（8 法索引）
  - MOMENT-MAGNIFIER.md、EFFECTIVE-INERTIA.md、PRESTRESS-LOSS-CALC.md 改為廢棄轉址 stub
  - 操作者：Cowork

- **[ARCHIVE]** raw/json/ 暫存檔歸檔至 study/_archive/
  - pdf_text.txt、pdf_2016_blocks.txt、pdf_2016_text.txt 已複製到 study/_archive/（附 README 說明）
  - 操作者：Cowork

- **[PENDING-DELETE]** 待刪除清單（沙箱環境因磁碟空間不足無法啟動，刪除作業暫緩）
  - raw/json/pdf_text.txt、raw/json/pdf_2016_blocks.txt、raw/json/pdf_2016_text.txt（已歸檔至 study/_archive/）
  - wiki/methods/MOMENT-MAGNIFIER.md、EFFECTIVE-INERTIA.md、PRESTRESS-LOSS-CALC.md（廢棄轉址 stub）
  - raw/solutions/RC-2015-1 ~ RC-2015-4 等資料夾內的 .placeholder 空檔
  - 檔名大小寫正規化：PM-INTERACTION-DIAGRAM.md → pm-interaction-diagram.md 等 5 檔（Windows 大小寫不敏感，連結已可解析，僅顯示名稱待改）
  - 環境恢復後對 Cowork 說「清理待刪除檔案」即可執行
  - 操作者：Cowork

---
**2026-06-28 compile-all**
- 修復 question_index.json（SD-2025-1~4 truncation）
- 生成概念頁 17 篇（wiki/concepts/SD-C-001 ~ SD-C-017）
- 生成題目頁 93 篇（wiki/problems/SD-YYYY-N.md）
- 更新 wiki/index.md（七層架構導覽）
- 更新 wiki/by-year.md（2002–2025 依年分類）
- 跳過 wiki/diagnosis/、wiki/failure-modes/、wiki/materials/、wiki/code-ref/、wiki/queries/（保持原狀）
- 跳過 raw/solutions/methods/（含 RC 方法，非 SD 科目）

---
**2026-06-28 cleanup-rc-clone**
- 刪除 wiki/problems/RC-*.md（100 個 RC 題目頁）
- 刪除 wiki/concepts/ 中的 RC 概念頁（25 個）
- 清除 wiki/methods/、wiki/philosophy/、wiki/traps/ 中所有 RC 頁面
- 清除 wiki/diagnosis/、wiki/failure-modes/、wiki/code-ref/ 中所有 RC 頁面
- 建立 SD 架構佔位頁（六個目錄各一個 index.md）
- 操作原因：本資料夾從 exam-wiki-RC 克隆，清除所有 RC 殘留內容

---
**2026-06-28 lint-optimize**
- CHECK 5 (viz未登錄)：17個wiki頁補上 viz HTML 連結
- CHECK 6 (spectrum-viz缺口)：建立 7 個反應譜互動圖（SD-2004-5/2012-1/2014-1/2016-4/2020-2/2020-3/2022-3）
- CHECK 7 (RC假陽性)：確認 raw/solutions/methods/ 全為 RC 方法，非 SD 科目，lint 排除
- CHECK 13 (diagnosis/)：建立 sdof.md / mdof.md / spectrum.md / code-design.md
- CHECK 14 (failure-modes/)：建立 resonance.md / excessive-drift.md / brittle-failure.md
- lint 16 項全數通過 🎉

---
**2026-06-28 refresh-dashboard**
- dashboard.html 完全改寫為 SD 科目版本（原為 RC clone）
- dashboard-data.js 重新生成：SD_TOPICS / SD_UNITS / SD_QUESTIONS / SD_META
- 統計：99 題，93 題已解析，21 題附互動圖
- 功能：題目瀏覽（搜尋/多維篩選/標籤過濾）、考點統計圖、知識導覽九格
- 2026-07-01 20:55:41 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-01 20:57:01 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-01 20:58:46 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-01 21:08:41 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-01 21:15:02 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-02 09:14:35 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-02 09:47:39 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 09:41:03 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 09:43:30 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 09:45:55 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 09:50:34 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 09:54:07 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 09:58:50 Ingested SD-2019-1
- 2026-07-03 09:58:50 Ingested SD-2019-2
- 2026-07-03 09:58:50 Ingested SD-2019-3
- 2026-07-03 09:58:50 Ingested SD-2019-4
- 2026-07-03 09:58:50 Ingested SD-2015-1
- 2026-07-03 09:58:50 Ingested SD-2015-2
- 2026-07-03 09:59:37 [REFRESH-DASHBOARD] Updated dashboard-data.js

---
**2026-07-03 ingest-fix（SD-2015-1、SD-2015-2、SD-2019-1~4）**
- 發現前次 09:58:50 的 6 筆 [Ingested] 紀錄為沙箱磁碟空間不足中斷後留下的失效紀錄：wiki/problems/ 實際僅有 SD-2015-1.md、SD-2015-2.md 兩檔，且內容為 raw 解析全文直接複製（非正確的 compile 摘要格式），SD-2019-1~4 四檔案完全不存在
- 重新執行完整 INGEST：
  - 重寫 wiki/problems/SD-2015-1.md、SD-2015-2.md 為標準摘要格式（題幹摘要／核心考點／解題關鍵步驟／用到的公式／涉及陷阱／相關題目）
  - 新建 wiki/problems/SD-2019-1.md、SD-2019-2.md、SD-2019-3.md、SD-2019-4.md
- 修復 wiki/index.md：
  - SD-2015-1、SD-2015-2 於 `SD-U1-3` 區塊的標籤空白 stub 補齊
  - 補上 SD-2015-1 於副分類 `SD-U1-1` 區塊、SD-2015-2 於副分類 `SD-U1-2` 區塊的交叉列表（先前完全缺漏）
- 確認 wiki/by-year.md 於 2015、2019 兩年份已正確標示 ✅ 六題，無需修改
- 未執行：wiki/concepts/ 各頁「出現題目」欄位反向連結（全庫 17 個概念頁自建立以來均為 placeholder，未曾針對任何一題實際填入，故此次維持與既有 93 題一致的現狀，不單獨為此 6 題破例）；wiki/traps/index.md（為精選陷阱彙整表，非逐題自動生成，維持現狀）
- 操作者：Cowork
- 2026-07-03 10:15:47 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 10:21:35 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-03 [REFRESH-DASHBOARD] 全量比對 question_index.json 與 dashboard-data.js，共 99 題，0 筆差異，資料一致
- 2026-07-03 10:35:00 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-10 [STUDY] 產生子題複習儀表板 study/study-SD-U1-1、U1-2、U1-3、U2-2、U3-2.html（共 5 頁，題目連結 171 筆，資料源 question_index.json 99 題）
- 2026-07-16 21:47:55 [REFRESH-DASHBOARD] Updated dashboard-data.js
- 2026-07-25｜REBUILD｜**重建 `CLAUDE.md` 與 `CLAUDE-CODE.md`**。稽核六科時發現這兩檔中文內容已因編碼轉換永久損毀（常用字比例僅 15% / 6%，且含 `?` 代表位元已遺失，經 big5 / cp950 / big5hkscs / gbk / latin-1 反解測試均無法還原）。損壞範圍已確認**僅限這兩檔**：99 份 raw 解析、140 頁 wiki、以及 `CLAUDE-SPEC.md` / `CLAUDE-SOLVE.md` / `README.md` 全部完好。
  處理方式：以 exam-wiki-SS 的乾淨結構為模板重建，SD 專屬內容取自未受損來源 —— 8 個單元名稱取自 `wiki/index.md`、分類代號取自 `raw/json/syllabus_taxonomy.json`、題數與分佈取自 `question_index.json`、科目全名與考卷命名慣例取自 `README.md` 與 `raw/exams/`。舊檔保留為 `CLAUDE.md.bak` / `CLAUDE-CODE.md.bak`。
  **順帶修正一項被亂碼掩蓋的錯誤**：損壞檔殘存的英文顯示原本科目識別寫的是「RC（Reinforced Concrete Design and Prestress）」—— 該檔係由 exam-wiki-RC 複製後未更改科目代碼，已改正為 SD（Structural Dynamics & Seismic Design）。
  重建後驗證：單元表與 question_index 的 8 個 topicId 完全一致；題數 99 相符；結構圖列出的 wiki 子目錄全部存在；25 份考卷命名慣例相符；無殘留 SS／鋼結構字樣；規則編號 1–8 連續。
- 2026-07-25｜HARNESS｜規則 1 例外擴充（六科統一）：`raw/` 唯讀的例外增列 `raw/solutions/methods/`，並明訂三個必要條件（① 數值驗算 ② 同步覆蓋 wiki/methods/ ③ 記 log）；`raw/solutions/SD-YYYY-N/` 明確排除在外。`CLAUDE-CODE.md` 於 ADD-METHOD 後新增 FIX-METHOD 五步流程與單位標註要求。本次為制度變更，未修改任何公式內容。
- 2026-08-09｜FORMULA-MAP｜產生 `study/formula-given-SD-U1-3.html`/`.pdf`（26 條，必背 16／別賭 6／通常會給 4）與 `study/formula-given-SD-U2-2.html`/`.pdf`（26 條，必背 15／別賭 7／通常會給 4）。證據來源：`raw/exams/` 2002–2025 全 24 份考卷 `pdftotext -layout` 全年份抽取，並對 14 個可疑年份轉圖逐頁目視判讀。影像頁修正兩處文字抽取誤判：① 106 年第一題的 `ω=√(k/M)`、`ω_D=√(1−ξ²)ω` 為影像，只看文字會誤判為「沒給」；② 96 年第一題 `F_u=√(2R_a−1)` 抽取後根號消失變成 `F_u=2R_a−1`。以 `scripts/verify.py` 交叉驗證卡片 ok 年份與逐年矩陣 ✔，兩頁皆 0 處矛盾。同步在 `lecture-SD-U1-3/U2-2.html` 與 `study-SD-U1-3/U2-2.html` 導覽列加入指向新頁的按鈕（雙向互連）。未修改 raw/ 任何檔案。
- 2026-08-09｜FORMULA-MAP｜再產生三個單元：`study/formula-given-SD-U1-1.html`/`.pdf`（24 條，必背 17／別賭 6／通常會給 1；零公式年 9／有題年 15）、`study/formula-given-SD-U1-2.html`/`.pdf`（22 條，必背 17／別賭 3／通常會給 2；零公式年 10／有題年 17）、`study/formula-given-SD-U3-2.html`/`.pdf`（23 條，必背 15／別賭 4／通常會給 4；零公式年 8／有題年 13）。證據沿用同一批 24 份考卷全年份文字抽取，並補做 2003／2010／2011／2012／2014／2017／2019／2023／2024 共 9 年的逐頁目視。**回頭修正 SD-U2-2 一處誤判**：101 年（2012）第二題圖二(b) 亦印出 \(B_S/B_1\) 四列數值表（該題屬 U3-2，但依「整卷共用」原則該年應計入有給），故「阻尼修正係數 B_S、B_1」卡片的 ok 由 [2011,2018] 改為 [2011,2012,2018]，逐年矩陣同步更新並重出 PDF。五份頁面全部通過 `scripts/verify.py` 交叉驗證（0 處矛盾），PDF 文字層無原始 LaTeX 外露、無 emoji 殘留。五個單元的 formula-given 頁已完成兩兩互連（PDF 按鈕固定最後一顆），並在對應的 `lecture-SD-*.html` 與 `study-SD-*.html` 導覽列加入指向按鈕。未修改 raw/ 任何檔案。
- 2026-08-09｜EXAM-INTEL｜以 `unit-exam-intel` 重構五份 `study/study-SD-U1-1／U1-2／U1-3／U2-2／U3-2.html`，由舊版七區段「深度複習頁」改為六區塊命題情報頁（出題概況／考點結構／考點漂移／題型走向／考題清單／命題風險）。**刪除的重複區段**：知識圖解（重複於 lecture §1）、解題流程圖（lecture §8–9）、必背公式（已被 formula-given 的給／背證據版取代）、高頻陷阱（lecture 陷阱總表）、Keynote 按鈕；**經使用者確認後刪除**互動測驗區段。**保留並擴充**：命題分析（原僅一段，擴為六區塊）、考題清單（補上全部副考點）。頁面每個數字均由 `scripts/stats.py` 從 question_index.json 算出，並以 `scripts/verify.py` 對帳（Q[] 題號集合、主副旗標、篩選鈕括號數、四個 KPI、題號連結、禁用寫法），五份全部通過。
- 2026-08-09｜PROBLEMS-VIEW｜新建 `study/problems-view/`，把全部 99 份 `raw/solutions/SD-YYYY-N/*.md` 渲染為自包含 HTML（python-markdown + 本機 KaTeX，數學式先抽出保護再還原，避免 `_`／`*` 被當成 markdown 強調）。每頁 header 有三顆返回按鈕（命題分析／觀念講義／給／背分界），並注入「跟隨來源單元」腳本：讀 `document.referrer`，若來源是 `study-`／`lecture-`／`formula-given-SD-Un-m.html` 就把三顆按鈕改指向來源單元；靜態 href 保底。取代舊版 `../index.html#md=raw/solutions/...`（該寫法只會顯示未渲染的純文字，五份舊 study 頁合計 171 個連結全部替換）。
  - 過程中發現並繞過（**未修改 raw/**）：`raw/solutions/SD-2007-2/`、`SD-2007-3/` 的附圖檔名少了開頭的 `S`（`D-2007-2-fig-1.png`），已用模糊比對指向正確檔案；`SD-2008-3-chart-1.png`、`SD-2017-4-fig-1.png` 兩張附圖確實不存在，頁面改顯示「尚未截圖存入」佔位框。這四筆建議由使用者補正。
- 2026-08-09｜EXAM-INTEL 命題觀察（皆可由 `stats.py` 複算）｜① **U1-3 是絕對主戰場**：43 題佔 43.4%，24 個考年全部出現、無任何空窗，近 6 考年 6/6 年共 11 題；重心由「SDOF 情境題」漂向「MDOF 矩陣與模態量標準流程」（E 群前段 6 → 後段 11），化約法主考點則自 102-3 起空窗 12 年。② **U2-2 主 17／副 20，副多於主**，出現 16 年、兩段空窗（2010–11、2016–17）；重心由「算 V」漂向「論述為什麼」，V 公式計算型主考點已空窗 18 年，三水準哲學卻連三次出現。③ **U1-2 主 10／副 18**，只出現 8 年、四段空窗，是本科最零散的單元——但 18 題副考點分佈在 17 個年份，等於每年 MDOF 題的第一小題。④ **U1-1 主僅 2 題（2.0%，排第七）但副 20 題**，主／副落差全科最極端，故該頁的兩張圖刻意改用「主＋副全部列入」繪製並於圖標題註明。⑤ **U3-2 主 13／副 6，是唯一主多於副的單元**，重心由「裝置原理論述」漂向「等效線性化迭代計算」（L 群前段 2 → 後段 4），2019–2022 空窗四年後 112 年一次回歸 50 分。
- 2026-08-09｜FIX｜**修正五份 `lecture-SD-*.html` 的考題連結未渲染問題**（使用者回報）。原連結為 `<a class="qlink" href="../wiki/problems/SD-YYYY-N.md">`，直接把 markdown 檔丟給瀏覽器，公式與附圖都不會渲染，只顯示純文字原始碼。已全數改為 `href="problems-view/SD-YYYY-N.html" target="_blank"`，共替換 **369 個連結**（U1-1 34、U1-2 87、U1-3 126、U2-2 85、U3-2 37），全部指向已存在的渲染頁，0 個死連結。順帶把 `problems-view/` 生成器補上「同資料夾補充檔（.pdf／.html）」的路徑改寫（原本只處理圖片副檔名），修好 `SD-2025-2` 指向 `SD-2025-2_補充_勁度矩陣.pdf` 的斷鏈。目前 `study/` 底下（含 99 頁 problems-view）已無任何指向 `.md` 的連結、無 `index.html#md=`、無 `javascript:history.back()`，全部 href 與 img src 目標皆存在。
- 2026-08-20｜FREQUENCY-MAP｜以 `subject-frequency-map` 產生 `study/frequency-SD.html`（單一自包含 HTML、無外部相依）。資料源 `raw/json/question_index.json` 99 題／24 考年（2002–2025）與 `raw/json/syllabus_taxonomy.json` 8 個子項；`build_frequency.py` 對帳通過（熱圖格子總和＝題庫總題數、每列總和＝該子項題數、三個單元小計相符），無孤兒 topicId。排名表最後一欄自動掃描 `study/` 判定教材是否存在；本庫記憶片放在 `study/recall-decks/` 而非 `study/` 根目錄，故偵測改為連子目錄一併 glob 並輸出相對路徑，五個記憶片連結已實測可開。headless Chromium 目視 QA：console 乾淨、兩個模式皆能重畫、tooltip 題號格式正確。
- 2026-08-20｜FREQUENCY-MAP 全科觀察（全部由 `build_frequency.py` 算出，可重跑複算）｜① **單元權重**：SD-U1 55 題（55.6%）／SD-U2 22 題（22.2%）／SD-U3 22 題（22.2%），最重的 U1 是最輕單元的 2.5 倍。② **前五名**：U1-3 43、U2-2 17、U3-2 13、U1-2 10、U3-1 9，合計 92 題佔 92.9%——讀完這五個等於覆蓋九成以上。③ **副>主 的工具型子項**：U1-1（主 2／副 20）、U1-2（主 10／副 18）、U2-1（主 1／副 9）、U2-2（主 17／副 20）；切到「主＋副」模式後 U1-1 該列由 2 變 22，只看主考點會嚴重低估它。④ **0 題子項**：無，8 個子項都至少當過一次主考點，沒有可整段跳過的。⑤ **教材四種齊全**（講義＋給／背＋命題分析＋記憶片）：U1-1、U1-2、U1-3、U2-2、U3-2；U2-1、U2-3、U3-1 尚未製作。
