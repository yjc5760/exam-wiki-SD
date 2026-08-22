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
- 2026-08-22｜FIX-SOLUTION｜**七題解析稽核與勘誤（SD-2016-4、SD-2014-1、SD-2011-2、SD-2013-3、SD-2025-3、SD-2020-3、SD-2021-2）**。使用者指定複查這七題，逐題以 `raw/exams/` 原卷（`pdftotext -layout` 全文＋含圖頁轉 160 dpi 目視）與獨立 Python 重算交叉驗證。**修正五處實質錯誤**：
  ① **SD-2011-2 §3.3 傳導率**：原寫「β > 1 → |TR| = 1/(β²−1) < 1（隔振效果）」並粗體結論「高速行駛時（β > 1）懸吊系統反而提供隔振效果」——**隔振門檻是 β > √2，不是 β > 1**。1 < β < √2 區間 TR = 1/(β²−1) > 1 仍為放大（例：β = 1.2 → TR = 2.27），只是相位反轉。已改為四列分區表（β<1／1<β<√2／β=√2／β>√2），補上 β=√2 時 TR≡1 與 ξ 無關的推導、隔振區「阻尼越大隔振越差」的取捨，以及換算成車速的門檻 v > √2·v_res。驗證方式：本庫 `study/lecture-SD-U1-3.html`（傳遞率曲線圖說「只有 r > √2 才有隔振效果」）、`problems-view/SD-2009-2.html`（L3 表「r>√2 時隔振」）、`SD-2005-4.html` 三處原本就寫對，本題為全庫唯一寫錯者，改後一致。順帶把「懸吊刻意設計高阻尼 ξ≈0.3~0.5」修為 ξ≈0.2~0.4 並補上其代價。
  ② **SD-2016-4 §4.2 反應譜讀值**：Mode 3（T₃ = 0.214 s）原讀 Sₐ = 0.80 g，實際該點落在譜的**上升段**。以 Pillow 對 `SD-2016-4-fig-2.png` 做像素反算（先由框線定出 x: T=0→119.5px、T=2.0→797px，y: Sₐ=0→490px、1.5→58px，再逐欄取最粗的暗色 run 為曲線），復原全條曲線：T=0.2→0.70g、0.25→0.79g、0.3→1.00g、0.4→1.21g、峰值 0.5→約1.27g、0.6→1.21g、0.7→1.01g、0.8→0.81g、0.9→0.63g、1.0→0.50g、2.0→0.12g。故 T₃=0.214 s 內插得 **0.72 g**（原 0.80 g 高估 11%）；T₁=0.800 s 的 0.80 g 正確、T₂=0.293 s 圖上 0.97 g 保留取 1.00 g。已重算 Mode 3 全鏈：Sd₃ 0.009142→0.008228 m、ΓSd₃ 0.0004083→0.0003675 m、{U₃}、慣性力 1752/−3034/1752 N→1577/−2732/1577 N、層剪力 1752/−1282/470 N→1577/−1155/422 N。**SRSS 最終答案不變**（位移 7.95／13.72／15.86 cm、層剪力 25.8／67.2／91.5 kN），因 Mode 3 有效質量比僅 0.5%（Mode 1 佔 92.9%）——已在 §4.2 寫入此「讀圖精度該花在哪個模態」的說明，並在 §6.2 常見錯誤表新增兩列。順帶把 Mode 1 的 f₂ 由 42,283 N 修正為 42,275 N，層剪力 66,690→66,682、91,097→91,089（原為 Γ₁ 取捨位差）。
  ③ **SD-2021-2 §5 爭議點 2 半正弦脈衝判斷表**：三個數字全錯。原表寫「t_d/T < 0.4 → R_d < 1」、「≈0.5 → ≈1.77」、「> 1.0 → 趨近 2（準靜態衝擊）」。以無阻尼 SDOF 對半正弦脈衝逐點數值積分（強迫相取 200,001 點取極值，自由相取端點振幅 √(x²+(ẋ/ω₀)²)，兩相取大者）得正確 SRS：t_d/T = 0.10→0.396、**0.159（本題）→0.621**、0.28→約1.00（R_d=1 的分界）、0.40→1.373、**0.50→1.571 = π/2（兩相交點，最大值由自由相移交強迫相）**、**0.81→1.768（全域尖峰）**、1.00→1.732、≫1→趨近 1。已改為八列表並加「三個常被記錯的點」：R_d<1 門檻是 0.28 不是 0.4；1.77 在 0.81 不是 0.5；長持續時間趨近 1 不是 2（R_d→2 是**突加定值載重 step load** 的結果，半正弦長脈衝載重緩變故趨近靜力解）。本題答案 6.22 cm 與 R_d = 0.622 經復算相符（精算 0.062168 m／0.6217），不變。另在 §4 Step 4 註明所用封閉解與 Duhamel 積分等價。
  ④ **SD-2020-3 §5 CQC 漸近式與交叉項量級**：原寫 S_jk ≈ 8ξ²r^{3/2}/r⁴ = 8ξ²/r^{5/2}——漏掉分子 (ξ_j + rξ_k) 自帶的一個 r，正確漸近式為 **8ξ²/r^{3/2}**（r=2.916 時 1.45×10⁻³，與精確值 2.49×10⁻³ 同量級；誤用 r^{5/2} 得 4.96×10⁻⁴，低估 5 倍）。另原寫交叉項「對總和的貢獻僅 −0.0006%」，實際 2S₁₂u₁u₂ = −5.93×10⁻⁶ m²，佔平方和 2.853×10⁻³ m² 的 **−0.21%**，開根號後對位移影響 **−0.10%**（0.05341→0.05336 m）；彙整表「差異 0.09%」改為 −0.10%。SRSS 5.34 cm 與 CQC 5.34 cm 兩個答案本身正確，不變。
  ⑤ **SD-2025-3 §5.4** 簡體字「务必」改為「務必」（全庫掃描確認無其他簡體殘留）。
- 2026-08-22｜FIX-SOLUTION（續）｜**新增的考卷原文勘誤（SD-2020-3，不影響答案）**：核對 109 年第三題振態表時發現**考卷本身印錯兩處**——振態1/1F 印 0.160（該列 Σφ² = 0.9967 ≠ 1，應為 **0.170**）、振態4/5F 印 +0.326（以印出值計 {φ₁}ᵀ{φ₄} = 0.385 違反正交性，應為 **−0.326**）。判別依據：均勻剪力構架解析振態 φ_j^(i) = C·sin[(2i−1)jπ/11]（n=5），正規化後量值集合恰為 {0.170, 0.326, 0.455, 0.549, 0.597}，原表五個振態的數字全部取自此集合，僅上述兩處數值／符號印錯。以更正值驗算 Σ L_i² = 5.001 ≈ M_total = 5 ✓，ρ 依序 88.0／8.7／2.4／0.8／0.2% 單調遞減；若照考卷印出值算，ρ₄ 會變成 14.3% 大於 ρ₂，明顯違反剪力構架物理。已寫入解析 §5「進階」並註明答案「採 2 個振態」（95.80% ≥ 95%）不受影響。同節另補：譜位移表的 ω 沿用考卷寫法但單位是 **Hz（即 f）不是 rad/s**，並以分段函數在 f=0.5、1.5 兩交界處皆連續（0.01+0.15×0.4 = 0.07 = 0.105/1.5）反證此讀法正確。
- 2026-08-22｜FIX-SOLUTION（續）｜**資料一致性與規格補正**：（a）檔內 verificationStatus 與 `question_index.json` 脫節者三筆已先對齊（隨後依同日 STATUS-RESET 一併退回 unverified，見下方該筆紀錄）——SD-2016-4（原 unverified）、SD-2013-3（原 unverified，並補上解得的公式與兩個極限驗核依據）、SD-2011-2（原 pending，非合法值）；SD-2016-4 的 hasViz 由 false 改為 true（`SD-2016-4-spectrum-viz.html` 確實存在，索引本來就是 true）。（b）**補上缺漏的附圖嵌入**：SD-2016-4 原文只寫「如 fig-1 所示」卻未依 CLAUDE-SOLVE.md 的雙重保險格式引用，已補 fig-1（三層剪力屋架）與 fig-2（線彈性反應譜，圖說含由像素反算所得的十個讀值）；SD-2011-2 補 fig-1（車輛 SDOF，並註明題圖記號為 u^t 而本文用 u′）。（c）補 `> 📊 互動圖` 行於 SD-2014-1、SD-2016-4、SD-2020-3（三題索引 hasViz 皆為 true 但正文未指向 viz 檔）。（d）SD-2013-3 §3.5 原缺 CLAUDE-SOLVE.md 標示「必須輸出」的 **L2：需知識點推導**段，已補四組表（形函數與導數／分子應變能／分母兩部分動能／組合）；§6 附圖狀態由「等待使用者截圖」改為「✅ 已存入」（檔案早已存在）。
- 2026-08-22｜FIX-SOLUTION（續）｜**經完整重算但未發現錯誤者**：**SD-2014-1** 全部正確——L₁=2430／M₁=2076.6／m₁*=2843.5 kg（原文 2843.6 為末位捨入，已修）、ρ₁=94.8%／ρ₂=5.3%、Sₐ(T₂=0.075)=0.155（上升段代式）、V_b=0.569 tf、ü₂=2.31 m/s²；黃金比例振態 {0.618,1}／{−1.618,1} 亦由等質量等勁度二層剪力構架特徵方程 λ²−3λ+1=0 復核相符，且 T₂/T₁ = √(0.382/2.618) = 0.382 與題給 0.075/0.20 = 0.375 一致。**SD-2013-3** 全部正確——以 `fractions.Fraction` 精算：∫φ²dx 係數 36/5−8+4−1+1/9 = 104/45 ✓、φ(L/2) = 17L⁴/16 ✓、整併常數 331,776／26,624／13,005 三者皆 ✓；兩個極限驗核 W→0 得 12.46 vs 精確 12.36（誤差 0.8%）、mL→0 得 25.51 vs 精確 24（誤差 6.3%，符合 Rayleigh 上界特性）。**SD-2025-3** 數值全部正確——a₀=1.10362 s⁻¹、a₁=1.6474×10⁻³ s、ζ₂=0.04336、ω*=√(ω₁ω₃)=25.88 rad/s，緊湊式 ζ₂ = ζ(ω₁ω₃+ω₂²)/[ω₂(ω₁+ω₃)] 復核相符。**SD-2016-4／2020-3／2021-2** 除上述五處外，特徵多項式 λ³−6λ²+9λ−2 = (λ−2)(λ²−4λ+1)、三組振態與正交性、模態參與因子、有效質量和 Σ=2.5m 與 5.0、95% 準則、S₁₂=0.00249、ξ=6%、x(t_d)=0.029805 m／ẋ(t_d)=0.5456 m/s 等全部復算相符。
- 2026-08-22｜FIX-SOLUTION（續）｜**下游同步**：（a）`study/problems-view/` 七頁重新渲染。渲染器先以未修改的 `SD-2016-4.md`／`SD-2011-2.md` 對既有 HTML 做**逐位元回歸測試**（保留 `<main>` 以外的 header／footer／跟隨來源單元腳本原封不動，body 以 python-markdown + tables/fenced_code、數學式先抽出占位再還原重建），確認兩頁 body 完全一致後才套用到修改後的內容；期間發現新版 python-markdown 已不允許清單直接中斷段落，故加入前處理補空行以重現原輸出。圖片路徑改寫為 `../../raw/solutions/<id>/`。（b）`wiki/problems/SD-2011-2.md` 的 verificationStatus 由 pending 改 verified（compile 摘要沿用了 raw 的舊值）；`SD-2016-4.md`、`SD-2011-2.md` 摘要補上附圖。（c）**順帶修好 compile 產物的斷圖**：`wiki/problems/` 的圖片連結原為 `SD-YYYY-N-fig-1.png` 相對路徑，從 `wiki/problems/` 出發必然 404，SD-2013-3、SD-2014-1、SD-2021-2 三頁已改為 `../../raw/solutions/<id>/`（此為 compile-all 產生器的既有缺陷，建議下次改產生器時一併修正，否則會被蓋回）。（d）`raw/json/question_index.json` 與 `dashboard-data.js` 均只存後設資料（tags／analysisMethod／verificationStatus／hasViz），本次修正未觸及這些欄位的值，故不需變更——已比對確認 hasViz 與實際 viz 檔存在狀況相符（verificationStatus 之變更見同日 STATUS-RESET 紀錄）。（e）`study/frequency-SD.html`、`study-SD-*.html`、`lecture-SD-*.html` 僅引用題號連結、不複製解析內容，無需同步。
- 2026-08-22｜STATUS-RESET｜**七題 verificationStatus 由 verified 重設為 unverified**（使用者指示）。範圍：SD-2016-4、SD-2014-1、SD-2011-2、SD-2013-3、SD-2025-3、SD-2020-3、SD-2021-2；其餘 92 題不變（`question_index.json` 現為 92 verified / 7 unverified / 0 needs-review）。理由：本次稽核修改過這七題的解析內容，原「verified」是針對舊內容的人工驗算結果，對修改後的版本已不成立，故一律退回 unverified 等待重新驗算——即使其中 SD-2014-1、SD-2025-3 的計算內容經復算完全正確、只動了排版與註記，仍一併重設以維持「內容一經改動即失效」的規則單純性。
  同步範圍：（a）`raw/json/question_index.json` 七筆 verificationStatus 改 unverified，`_meta.updatedAt` 改 2026-08-22 並在 notes 註明退回原因與回復條件；以純文字定點取代而非 JSON round-trip，保留原檔 CRLF 行尾與 2 空白縮排，全檔 diff 僅 9 行。（b）七份 `raw/solutions/*/SD-*.md`：原本只有三份有狀態註記（且格式各異、其中 SD-2011-2 用的 `pending` 並非合法值），已統一為檔尾三列表格（verificationStatus／hasSolution／hasViz）＋一行「驗證狀態備註」說明為何退回；SD-2011-2 保留其題首資訊表內的欄位、SD-2013-3 保留其 §6 既有寫法，兩者一併改為 unverified。SD-2013-3 的 `verifiedSolution` 改標為「AI 解得（待人工驗算，驗算通過後方可填入 verifiedSolution）」——尚未經人工驗算的結果不應佔用 verifiedSolution 欄位。（c）七份 `wiki/problems/SD-*.md` 的「驗證狀態」徽章由 ✅ verified 改為 ⚠️ unverified。（d）`study/problems-view/` 七頁重新渲染。
  **未變更且理由**：`dashboard-data.js` 的每筆資料列格式為 `[moduleId, primaryTopicId, secondaryTopicIds, analysisMethod, viz, tags, pdf]`，不含 verificationStatus 欄位，故無需重生成（驗證統計由 `status` 指令即時讀 `question_index.json`，不吃這支快照）。
  **已知副作用（提醒）**：CLAUDE.md 規則 5「ingest 前必須確認 verificationStatus = verified」——這七題的 `wiki/problems/` 頁面是在先前 verified 狀態下 ingest 的，現狀為「已 ingest 但 unverified」。本次選擇保留既有 wiki 頁（僅改徽章）而非撤回，因撤回會讓 `wiki/index.md`、`by-year.md` 出現七個缺口、反而更難追蹤；人工驗算通過後把七筆改回 verified 即回到一致狀態。若之後對這七題重跑 ingest，會被規則 5 擋下，屆時先完成驗算再執行。
- 2026-08-22｜STATUS-RESET（全庫）｜**全庫 99 題 verificationStatus 一律重設為 unverified**（使用者指示，範圍由前一筆的 7 題擴大到全部）。`question_index.json` 現為 0 verified / 99 unverified / 0 needs-review。
  變更明細：（a）`raw/json/question_index.json` 92 筆 `"verified"` → `"unverified"`（前 7 筆已於同日先前重設），並在 `_meta.notes` 追記全庫重設一事；同樣以純文字定點取代、保留 CRLF 與 2 空白縮排。（b）`wiki/problems/` 92 份徽章 `✅ verified` → `⚠️ unverified（2026-08-22 全庫重設，待人工驗算）`，全 99 份現已一致。（c）`raw/solutions/` 有 8 份的檔內標記寫的是 **`pending`**（SD-2011-1／3／4、SD-2012-1～4、SD-2013-4）——`pending` 並非合法值，本次一併正規化為 `` `unverified` ``；連同前次的 11 份，19 份帶標記的解析現已全為 unverified。（d）`study/problems-view/` 對應的 8 頁把 `<td>pending</td>` 改為 `<td><code>unverified</code></td>`（該處為單一字串取代，與 .md 變更同構，故直接改渲染層而未重跑渲染器）。
  **未變更且理由**：（i）其餘 80 份 `raw/solutions/*/SD-*.md` **本來就沒有** verificationStatus 檔內標記（99 份中僅 19 份有），本次不逐一補上——依 CLAUDE.md「索引資訊唯一來源：`raw/json/question_index.json`」，檔內標記只是輔助顯示，補 80 份會製造大量非必要 diff、且日後與索引再次脫節的機會更多。（ii）`dashboard-data.js` 資料列不含 verificationStatus 欄位，無需重生成。
  **順帶發現的既有問題**：這 19 份檔內標記在本次之前就與索引嚴重脫節——索引當時 99 題全為 verified，但檔內卻有 8 份寫 `pending`、11 份寫 `unverified`，等於沒有一份對得上。這說明檔內標記從未被 ingest／compile 流程同步過。建議後續要嘛讓 compile-all 自索引回填這個欄位、要嘛乾脆從 .md 移除該欄位只留索引一處，否則每次改狀態都要手動掃兩地。
  **狀態**：全庫現無任何 verified 題目，依 CLAUDE.md 規則 5，此刻對任何一題執行 ingest 都會被擋下；這是預期行為，人工驗算通過後逐題改回 verified 即可解除。

- 2026-08-22｜收工｜完成 7 題解答內容修正重算、全庫狀態退回 unverified，並更新渲染產物。備份檔 (.bak) 予以忽略，其餘相關修改與腳本/繪圖檔案皆已提交。

- 2026-08-22｜FIX-SOLUTION（第二批八題）｜**使用者指定複查 SD-2010-1、SD-2004-4、SD-2009-1、SD-2011-3、SD-2017-2、SD-2016-2、SD-2023-1、SD-2002-1**。方法：以 `raw/exams/` 原卷（`pdftotext -layout` 全文；2002／2004／2009 三份 PDF 的中文為 CID 造字、文字層與轉圖皆無法還原，故該三題改以「題目附圖逐像素判讀＋數值一致性＋物理極限」交叉驗證）、附圖放大目視、以及獨立重算三路對帳。**發現三處實質錯誤、四處敘述性錯誤，全部已修**：
  ① **SD-2016-2（最嚴重，答案錯）｜漏算一根彈簧**。附圖上排標註為「$l/2\ k\ l/2\ k$」，代表上梁**中點與右端 B 各有一根天花板彈簧**，B 點另有向下的聯接彈簧——即 B 為「一點兩簧」，全系統共 4 根彈簧。原解只計入中點那一根，得 $K_{11}=5kl^2/4$，矩陣退化為 $\begin{bmatrix}5/4&-1\\-1&5/4\end{bmatrix}$、特徵值 $1/4$ 與 $9/4$、並得出「$\omega_2=3\omega_1$、振態 $\{1,1\}$ 與 $\{1,-1\}$」這組**看似漂亮實則錯誤**的答案。更正後 $K_{11}=9kl^2/4$、$K_{22}=5kl^2/4$、$K_{12}=K_{21}=-kl^2$；特徵方程 $16\lambda^2-56\lambda+29=0$ → $\lambda=(7\mp2\sqrt5)/4$；$\omega_1=\tfrac12\sqrt{(21-6\sqrt5)k/m}\approx1.377\sqrt{k/m}$、$\omega_2=\tfrac12\sqrt{(21+6\sqrt5)k/m}\approx2.933\sqrt{k/m}$（$\omega_2/\omega_1\approx2.13$）；振態 $\{1,\tfrac{1+\sqrt5}{2}\}$ 與 $\{1,\tfrac{1-\sqrt5}{2}\}$（黃金比例，兩者正交 ✓）。三重驗算：Vieta（跡 $=14/4$、行列式 $=29/16$）、Rayleigh 商反查（$2.2865/1.2060=1.896=\omega_1^2 m/k$ ✓）、量綱（$l$ 相消，頻率與梁長無關 ✓）。同步重繪 `SD-2016-2-modal-viz.html`（補畫 B 端天花板簧、改正上下梁相對位置、改用正確振態比與頻率、加註更正說明）。
  ② **SD-2004-4（答案錯）｜尺寸線誤讀**。原解把 $h_2$ 當成「$m_1$ 到 $m_2$ 的段長」，故轉動地震影響向量寫成 $\{l_\theta\}=\{h_1,\,h_1+h_2,\,x_3\}^T$。逐像素檢視 `SD-2004-4-fig-1.png`：$h_2$ 尺寸線自 $y=590$（地面）延伸至 $y=165$（梁），$h_1$ 尺寸線自 $y=590$ 延伸至 $y=378$（$m_1$）——**兩條同起於地面**，且 $m_1$ 恰位於全高中點（$378=(165+590)/2$），故 $h_1$、$h_2$ 皆為離地高度。更正為 $\{l_\theta\}=\{h_1,\,h_2,\,x_3\}^T$，連帶更正 §1 系統描述與 ASCII 圖、§1 圖說、§2 陷阱、§3 作戰計畫、§3.5 Step 3c／L1／L2 表、§4 子題(三)表格與物理驗算。$[M]=\mathrm{diag}[m_1,m_2+m_3,m_3]$ 與 $\{l_x\}=\{1,1,0\}^T$ 復算正確，未動。§5 新增「尺寸線的讀圖教訓」把本次錯誤轉為可複習的判準。
  ③ **SD-2017-2（符號錯）｜轉角慣例與勁度交叉項的對應關係整組寫反**。附圖 $v_2$、$v_3$ 的弧形箭頭（放大至 8 倍檢視）自左上起、繞右下收尾，為**順時針**。但 $v_1$ 取向右為正時，正確關係是「**CCW 正 → $K_{12}=+6EI_1/h^2$；CW 正 → $K_{12}=-6EI_1/h^2$**」，原文卻寫成相反、並以「CW 正使矩陣全正、便於驗算」為由採用。以傾角變位法獨立推導：固定–固定柱純側移 $\Delta$ 時弦順時針轉（$\psi=-\Delta/h$），$M=\frac{2EI}{h}(0+0-3\psi)=6EI\Delta/h^2$ 為**逆時針**，故 CW 正慣例下為負。更正 $[k_{col}]$、$[K]$、三道分量方程與矩陣展開式為 $K_{12}=K_{13}=-6EI_1/h^2$。連帶更正 §5.1 靜態凝縮：$v_2=v_3=+\frac{6EI_1/h^2}{4EI_1/h+6EI_2/\ell}v_1$（**正值**，代表節點順時針轉，與「門形框架右移時節點順時針轉」相符；原文為負值，與物理矛盾），並補上原本缺漏的 $k_{\text{eff}}=\frac{24EI_1}{h^3}-\frac{72E^2I_1^2}{h^4(4EI_1/h+6EI_2/\ell)}$ 及兩個極限驗算（$EI_2\to\infty$ 得 $24EI_1/h^3$＝剪力構架；$EI_2\to0$ 得 $6EI_1/h^3$＝兩根懸臂柱並聯 $2\times3EI_1/h^3$）。§5.2 改為 CW／CCW 對照表並註明兩者僅差座標變換 $[T]=\mathrm{diag}(1,-1,-1)$、特徵值相同。$[M]=\mathrm{diag}(m,0,0)$、$K_{11}=24EI_1/h^3$、$K_{22}=K_{33}=4EI_1/h+4EI_2/\ell$、$K_{23}=2EI_2/\ell$ 復算正確。
  ④ **SD-2023-1（推導中間式與方框答案矛盾）**。§4 第(一)題以 $w$ 向下為正，卻寫 $M=EI\,w''$、$V=EI\,w'''$，再套用同段的 $\partial V/\partial x+P\delta=\bar m\ddot w$，實際會導出 $\bar m\ddot w-EI\,w''''=P\delta$，與下方方框的 $+$ 號相反。$w$ 向下為正且 $M$ 取下側受拉為正時，曲率關係必須是 $M=-EI\,w''$（中央下垂處 $w$ 極大、$w''<0$ 而 $M>0$）。已更正中間式（含 L2 表），並新增靜力極限驗算：均布載重下退化為 $EI\,w''''=\bar q$，代入簡支梁靜撓度 $w=\frac{\bar q}{24EI}(x^4-2Lx^3+L^3x)$ 得 $w''''=\bar q/EI$ ✓。方框答案與第(二)(三)小題（$\beta_n=n\pi/L$、$\omega_n=\frac{n^2\pi^2}{L^2}\sqrt{EI/\bar m}$、$\phi_n=\sin\frac{n\pi x}{L}$、$M_n=\bar mL/2$、$Q_n=P(t)\sin\frac{n\pi}{2}$）復算全部正確。
  ⑤ **SD-2011-3（格式不合規）**。原檔採「題目資訊／解題步驟／驗算」自訂結構，缺少 CLAUDE-SOLVE.md 標示「必須輸出」的 **§3.5 變數層次分析**，與其餘 98 份不一致。已全文改寫為標準五節＋§3.5。另修正一處錯誤敘述：原陷阱表寫「特解猜 $u_p=Ct^2$（適用於常數激振力）」——常數力的特解是常數，不是 $Ct^2$。新增相對座標驗算（令 $w=u-vt$ 得 $m\ddot w+kw=0$、$\dot w(0)=-v$，解得同一答案）、量綱驗算與含阻尼討論。計算主體 $m\ddot u+ku=kvt$、$u(t)=vt-\frac{v}{\omega_0}\sin\omega_0 t$ 復算正確。
  ⑥ **SD-2002-1（敘述與驗算依據）**。（a）$k_\theta$ 單位 `kN-m` 補正為 `kN-m/rad`。（b）$L$ 原述「樓版質心至基座質心距離」與附圖不符（圖中 $L$ 標於地表至樓版之間），改為「基座旋轉中心至樓版之高度」並加註模型化假設。（c）結果彙整的驗算原用 $\sqrt{k_\theta/(I_1+I_2)}=31.6$ 作為特徵值界限——交錯（interlacing）界限必須用勁度矩陣對角元 $\sqrt{K_{11}/M_{11}}=\sqrt{1.254\times10^7/12000}=32.3$（含 $2kL^2$），原式漏掉柱的抗傾覆貢獻，只是巧合仍落在區間內；已改正並保留 31.6 作為「純搖擺頻率」的量級參考。（d）振態物理意義補上與剛體隨動量 $u_2=L\theta_1=3$ m/rad 的比較，作為「側移主導／搖擺主導」的判準。主體計算（$[M]$、$[K]$、$\omega^4-1645\omega^2+6\times10^5=0$、$\omega_1=23.4$、$\omega_2=33.2$、振態 $33.27$／$-3.61$）復算全部正確。
  ⑦ **SD-2009-1、SD-2010-1｜計算全部正確，僅修敘述**。SD-2009-1：L3 表原寫「若 $\Psi(L)=1$，則 $p^*=\bar pL$」自相矛盾（本題 $\Psi(L)=1$ 但 $p^*=0.375\bar pL$），改為「只有 $\Psi\equiv1$（剛體平移）時才等於 $\bar pL$」；$m^*=33\bar mL/140$、$k^*=3EI/L^3$、$p^*=3\bar pL/8$ 與 Rayleigh 估值 $3.567$ vs 精確 $3.516$（+1.5%，符合上界）皆復算相符。SD-2010-1：陷阱 ❸ 原文「彈簧力矩臂為 $L\cos\theta\approx L$，不是 $L$」語意矛盾，改寫為彈簧（水平力→力臂 $L\cos\theta$）與重力（鉛垂力→力臂 $L\sin\theta$）的對照；另新增 §5.3「臨界之後：非零平衡位置」（$\cos\theta^*=mg/(kL)$ 為不穩定分支，$k\to mg/L$ 時與 $\theta=0$ 合併＝分岔點）。穩定條件 $k>mg/L$、$mL^2\ddot\theta+(kL^2-mgL)\theta=0$、$\omega=\sqrt{k/m-g/L}$ 以位能法與力矩法雙路復算相符。
  **下游同步**：`wiki/problems/` 的 SD-2004-4（$h_2$ 敘述與 ASCII 圖）、SD-2016-2（彈簧清點、作戰計畫、陷阱表首列、標籤）、SD-2017-2（轉角慣例、圖說、陷阱表）、SD-2011-3（以新格式重寫題幹摘要／解題步驟／陷阱，並清掉殘留的非法值 `pending`）、SD-2002-1（$L$ 敘述與 alt text）五頁已同步；八題的 verificationStatus 本就全為 unverified（2026-08-22 全庫重設），內容既經改動仍維持 unverified，不需變更 `question_index.json`。`dashboard-data.js` 不含受影響欄位，未動。
  **一併記錄的工具限制**：`SD-2002`、`SD-2004`、`SD-2009` 三份考卷 PDF 的中文字元在文字層與 160 dpi 轉圖中皆為空白（字型子集未內嵌 ToUnicode，非編碼可解），只有數字、英文與 LaTeX 記號可還原。這三題的題意核對因此完全倚賴 `-fig-1.png` 附圖與數值，屬本次驗證中證據強度最弱的一環；若日後取得可讀版本的考卷，建議優先重核 SD-2002-1 的 $L$ 定義。

- 2026-08-22｜STRUCT-DIAGRAM｜**為上述八題補繪向量圖解**（`struct-diagram` skill）。共 16 張圖，一律以 Python 程式碼繪製 SVG（非 AI 生圖），圖上每個數值與比例都由解題結果算出、可重跑審核；輸出 `raw/solutions/<題號>/figs/*.svg`（給 HTML wiki 與 WeasyPrint）＋同名 2× PNG（給 pptx／影片管線），產圖腳本 `gen_<題號>.py` 隨解析一起版控。`render.py` 的 XML 合法性與溢出檢查全部 0 錯，並逐張目視確認（文字未重疊、無中文缺字方框、變形與轉角方向正確）。
  **每題與各圖攔下的錯誤**：SD-2002-1 ①自由度與柱變形 $\Delta=u_2-L\theta_1$（攔「柱變形寫成 $u_2$」）②兩振態形狀，以剛體隨動量 $L\theta_1=3$ m/rad 為判準（攔「側移／搖擺主導判反」；兩格共用同一 $\theta_1$，$u_2$ 長度比即特徵向量比）。SD-2004-4 ①幾何重繪，把 $h_1$、$h_2$ 兩條尺寸線的共同起點釘在地面（攔本次勘誤的 $h_1+h_2$）②兩種支承運動下的剛體位移（攔 $u_3$ 符號）。SD-2009-1 ①$\Psi$／$L\Psi'$／$L^2\Psi''$ 三聯圖（攔「$k^*$ 用一階導數」，同時把 $\Psi'(0)=0$、$\Psi''(1)=0$ 兩個邊界條件畫出來）②廣義量與總量的量級比較（攔「以為 $p^*=\bar pL$」）。SD-2010-1 ①自由體圖，彈簧力臂 $L\cos\theta$ vs 重力力臂 $L\sin\theta$（攔本次勘誤的力臂互換）②位能曲線在 $r=kL/mg$ 取 1.60／1.00／0.55 三種情形下的谷／平／峰（攔穩定條件方向）。SD-2011-3 ①靜平衡消去示意（攔「重力重複計入」與「彈簧變形只寫 $u$」）②無因次響應時程（攔「以為 $u(t)=vt$ 沒有振盪」，並顯示速度在 $0\sim2v$ 間、平均為 $v$）。SD-2016-2 ①四根彈簧逐點清點、B 點「一點兩簧」以虛線圈標出（攔本次最嚴重的漏簧）②兩個單位轉角狀態逐格算力矩（攔 $K_{11}$ 少一項與 $K_{12}$ 符號）③兩振態真實形狀 $\{1,1.618\}$／$\{1,-0.618\}$（攔「振態是 $\{1,\pm1\}$、$\omega_2=3\omega_1$」）。SD-2017-2 ①三個單位位移狀態（攔本次勘誤的 $K_{12}$ 符號；狀態 1 直接畫出「須外加逆時針力矩」）②側移變形形狀，柱雙曲率、節點順時針轉、反曲點由 §5.1 公式算出（攔符號慣例）。SD-2023-1 ①前四模態，標出 $n-1$ 個內部節點與中點值（攔「偶數模態為何不被激發」）。
  **繪圖過程中修掉的三個技術陷阱**（供日後重跑參考）：（a）`Noto Sans CJK` 缺下標字元 `₀₁₂₃`，混在中文字串裡會渲染成方框——已全部改為 `h1`、`ω0` 之類的 ASCII 寫法，並加自動掃描確認 0 處殘留；上標 `²` 與長音符 `̄` 則正常可用。（b）`cv.dim()` 的標籤走數學襯線字型，放中文會整段消失——改為只放符號，中文另以 `text_px` 標註。（c）函數圖若直接把「像素 y」餵給 `cv.poly()`，會被 Canvas 的 y 軸翻轉再翻一次而上下顛倒（SD-2010-1 位能圖初版即如此，穩定與不穩定看起來剛好相反）——已改為全程使用模型座標（y 向上）。
  **未更動**：`wiki/problems/` 的八個頁面為 compile 摘要、不含圖片區塊，本次不注入（下次 `ingest` 會自 raw 帶入）；`question_index.json` 的 `hasViz` 僅登錄 `*-viz.html` 互動圖，SVG 靜態圖不屬該欄位範圍，故不變更。八題 verificationStatus 維持 unverified。

- 2026-08-22｜DOWNSTREAM-SYNC｜**下游同步稽核與補正**（使用者要求：檢查修正後的 .md，其下游是否跟著更新；範圍含前一日已改動的 .md）。稽核方法不倚賴檔案時間（易誤判），改用三重證據：① `git diff --numstat -w` 找出相對上次 commit 真正有內容變更的檔案；② 比對 commit `31e655c` 實際涵蓋的下游檔案清單；③ 以「舊值探針」直接在下游檔案中搜尋已被更正掉的字串。
  **稽核結論**：（a）相對上次 commit，`raw/solutions/` 僅本次八題有內容變更，前一日那批（19 份 .md）已連同下游一起 commit。（b）但 commit `31e655c` 的 `study/problems-view/` 只涵蓋 15 頁，**漏了 SD-2006-1、SD-2013-1、SD-2020-1、SD-2023-2 這 4 頁**——這 4 份 .md 在該 commit 內確有實質修改（SD-2006-1 補齊 $\dot x_h$ 的 $\sin$ 項係數化簡並新增 3 張 svg；SD-2013-1 更正對數衰減率定義並加註「$S_a\propto1/T$ 只在下降段成立、折減比分子是 $T_s$ 不是 $T_0$」；SD-2020-1 改以「傳遞力」推導絕對加速度；SD-2023-2 修正模態質量／勁度的位數與 $\Gamma_2$），卻未重新渲染。（c）另 7 頁（SD-2011-2 等）雖檔案時間看似落後，但舊值探針顯示內容其實正確，屬誤判。
  **本次補正**：
  ① **重建 problems-view 渲染器並重新渲染 12 頁**（本次八題 ＋ 上述漏掉的 4 頁）。渲染器腳本未進版控，故依既有頁面結構重建：只替換 `<main>…</main>`，header／footer／跟隨來源單元的腳本原封不動；body 以 python-markdown（tables + fenced_code）產生，數學式先抽出佔位再還原，圖片與同資料夾附檔路徑改寫為 `../../raw/solutions/<題號>/`。**回歸測試**：對「自上次渲染後 .md 未再變動」的 6 頁重算，全部逐位元相同才套用。過程中復原出舊渲染器的兩條前處理規則——(i) 清單直接中斷段落時補空行（新版 python-markdown 不再自動接受）、(ii) 含巢狀子清單的清單，其頂層項目間補空行（舊版會整串轉成 loose list）。唯一未能完全重現的是 `SD-2012-3` 巢狀清單的鬆散度（差 18 bytes，純 `<li>` vs `<li><p>` 排版），該頁 .md 未變動故不重新渲染。渲染後檢查 12 頁：shell 完整、`$` 成對、圖片路徑全部可解析、0 異常。
  ② **`wiki/problems/SD-2013-1.md`**：摘要仍寫舊定義「對數衰減率是**連續兩峰值之比**的自然對數，而非相對比值」，已同步為 .md 現行敘述（相鄰兩峰值「比值」的自然對數 $\ln(x_n/x_{n+1})$，不是差、也不是衰減百分比），共 2 處。其餘 11 題的 `wiki/problems/` 摘要經探針檢查與 raw 一致（被改動的字句多半不在摘錄視窗內）。
  ③ **`wiki/by-year.md` 全庫 99 題的 ✅ 改為 ⚠️**。前一日的 STATUS-RESET 把 `question_index.json` 與 `wiki/problems/` 徽章都改成 unverified，但漏了 by-year.md，導致該頁 99 題全部仍顯示 ✅、與索引 100% 不一致。
  ④ **修好 compile 產物的斷圖，範圍擴大到全庫**：`wiki/problems/` 的圖片連結原為 `SD-YYYY-N-fig-1.png` 相對路徑，自 `wiki/problems/` 出發必然 404。前次僅修了 3 頁，本次一次修完 **43 頁、44 個連結**，現全庫 0 個斷圖。⚠️ 這是 compile-all 產生器的既有缺陷，若不改產生器，下次 compile 會被蓋回。
  ⑤ **`question_index.json`：SD-2016-2 標籤更正** —— 移除 `對稱結構`、`模態對稱反對稱`（本次已證實該結構並不對稱、振態也非對稱／反對稱），改為 `直接勁度法`、`黃金比例振態`；`轉動慣量`、`聯接彈簧` 保留。檔案以純文字定點取代，保留 CRLF 與 2 空白縮排，全檔 diff 僅 4 行。
  **經確認不需變更**：`wiki/index.md`（顯示的標籤與分析方法皆取自 `question_index.json`，非 .md 檔頭，且無驗證徽章）；`dashboard-data.js`（資料列不含解題內容與 verificationStatus）；`study/study-SD-*.html`、`lecture-SD-*.html`、`frequency-SD.html`（只引用題號連結）；`檔案架構索引表.md`（只列題號格線，不列個別檔案）。另 `.md` 檔頭的 `**標籤：**` 與索引 tags 全庫本就不一致（抽查 7 題皆然，非本次造成）——依 CLAUDE.md「索引資訊唯一來源：`question_index.json`」，檔頭標籤僅為輔助顯示，本次不逐一對齊，但建議後續讓 compile-all 自索引回填、或乾脆從 .md 移除該欄位只留索引一處。
  **狀態**：本次八題與前一日 4 題的 verificationStatus 一律維持 unverified。

- 2026-08-22｜DOWNSTREAM-SYNC（續）｜**順帶修好兩個既有的附圖檔名錯誤**：`raw/solutions/SD-2007-2/` 與 `SD-2007-3/` 的題目附圖實際檔名為 `D-2007-2-fig-1.png`、`D-2007-3-fig-1.png`（**開頭少了 S**），與 .md 中的引用不符，導致 `wiki/problems/` 與 `problems-view` 兩層皆斷圖；已更名為正確的 `SD-2007-2-fig-1.png`、`SD-2007-3-fig-1.png`，兩處斷圖解除。
  **仍待人工補件（非本次可修）**：`SD-2008-3` 的 .md 引用 `SD-2008-3-chart-1.png`，但資料夾內只有 `SD-2008-3-fig-1.png`——需確認是引用寫錯還是圖表截圖未存入；`SD-2017-4` 的 .md 引用 `SD-2017-4-fig-1.png`，但該資料夾**完全沒有任何 PNG**，需補截圖。這兩題不在本次修正範圍，僅登錄待辦。

  更名後補記：舊版 `problems-view` 產生器在改寫圖片路徑時會**吃掉題號開頭的 S**（`SD-2007-2.html` 內寫的是 `.../SD-2007-2/D-2007-2-fig-1.png`），這正是當初檔案被存成 `D-2007-2-fig-1.png` 的原因——兩個錯誤互相抵銷，故該頁一直「看起來正常」，反而是 `wiki/problems/` 那層斷圖。本次把檔名改正後，這兩頁的舊路徑失效，已用新渲染器重跑 `SD-2007-2`、`SD-2007-3` 兩頁，兩層路徑現皆指向正確檔名。全庫斷圖由 48 處降為 2 處（僅剩 SD-2008-3、SD-2017-4 的缺截圖待人工補件）。

- 2026-08-22｜DOWNSTREAM-SYNC（第二輪：摘要層）｜**使用者複問「這八題改完 .md 後下游是否已修正」，複查發現前一輪只做到渲染層，`wiki/problems/` 摘要層仍是舊產物。** 前一輪對摘要層只做了「把錯誤字句手動改掉」的局部補丁，並未重新生成，因此頁面仍夾雜舊段落（SD-2016-2 有 22 句、SD-2011-3 有 12 句在現行 .md 中已不存在；SD-2010-1 的陷阱 ❸ 仍是舊敘述）。
  **重建 compile-all 的 `wiki/problems` 產生器**（腳本同樣未進版控，規則由 99 頁既有產物反推）：題幹摘要＝raw `## 1.` 章節截斷至 **600 字元**（18 頁命中此上限）、解題關鍵步驟＝`## 3.` 章節截斷至 **400 字元**、涉及陷阱＝與解題關鍵步驟相同的擷取（83/93 頁完全相同）、用到的公式與圖形／相關題目沿用既有、標頭與核心考點由 `question_index.json` 生成、圖片路徑改寫為 `../../raw/solutions/<題號>/`。**回歸測試 75/93 頁逐位元相同**後才套用。
  **已重新生成 8 頁**：SD-2002-1、SD-2004-4、SD-2009-1、SD-2010-1、SD-2011-3、SD-2016-2、SD-2017-2、SD-2023-1。驗證：每頁摘錄字句 100% 可在現行 .md 溯源（0 孤兒）、圖片連結全部可解析、關鍵更正皆已反映。
  ⚠️ **過程中的事故與復原**：寫入時誤用 `io.open(path,'w').write(build(qid))` —— Python 先求值 `open('w')` 而截斷檔案，再呼叫 `build()` 去讀「已被清空的」同一檔案，導致 `wiki/problems/SD-2010-1.md` 被清為 0 bytes。已自 `git show HEAD:` 復原（3765 B）、重新套用圖片路徑修正後正常重生成（3811 B）。腳本已改為先產生內容再開檔。（註：本環境的 device_bash 無法 unlink，故 `git checkout --` 無法還原被截斷的檔案，只能用 `git show > 檔案` 覆寫。）
  **順帶查出、尚未處理的其他不同步頁（不在本次委託範圍，僅登錄）**：
  （a）**產生器可修的 8 頁**：SD-2013-1（-76）、**SD-2013-3（+263：缺前一日新增的向量圖 圖 1，該圖說點出「集中重量在 L/2 而非自由端」與「W 是重量、代入動能須寫 W/g」）**、SD-2015-1（-512）、SD-2015-2（-825）、SD-2019-1～4（-341／-220／-630／-249）。其中 SD-2015、SD-2019 兩組的摘要明顯取自更舊版本的 .md（現有頁面比重生成的長），推測是 `198d521` 之後 .md 有更新但未重跑 compile。
  （b）**舊式 .md 格式、產生器不適用的 10 頁**：SD-2011-1／2／4、SD-2012-1～4、SD-2013-4、SD-2016-4、SD-2016-5 —— 這些 .md 沒有 `## 1.` 標準章節（用的是自訂的「題目資訊」表格式），其 `wiki/problems` 摘要因此直接抄該表，也是 **7 頁殘留 `verificationStatus | pending`** 的來源（前一日的 STATUS-RESET 只改了 raw 與徽章，沒改摘要內的表格）。要根治需先把這 10 份 .md 轉為標準格式（如同本次對 SD-2011-3 所做），或讓產生器支援舊格式。
  **本次仍維持不變**：八題 verificationStatus 一律 unverified。
