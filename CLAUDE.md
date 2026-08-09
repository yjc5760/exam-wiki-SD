# 結構工程技師考試知識庫 — 結構動力分析與耐震設計（SD）

> 科目代碼：SD｜資料夾：`exam-wiki-SD`｜其他科目另建獨立資料庫

## 專案說明

本資料庫專門收錄「專門職業及技術人員高等考試結構工程技師」**結構動力分析與耐震設計**的考古題解析知識庫。

- **科目代碼：** SD（Structural Dynamics & Seismic Design）
- **題目編號格式：** SD-YYYY-N（如 SD-2018-1）
- **收錄範圍：** 2002–2025 年（民國 91–114 年）
- **其他科目：** 各自建立獨立資料庫（exam-wiki-SS、exam-wiki-RC、exam-wiki-SA、exam-wiki-SM、exam-wiki-MM）

**核心工作流程：**
```
在 Cowork 開啟 exam-wiki-SD/ 資料夾（Project）
    ↓
說：「解析 XXXX 年考卷」
Cowork 讀取 CLAUDE.md + 考卷 PDF + question_index.json
  → 建立所有尚無解析的題目資料夾（已有解析者跳過）
  → 提醒你將各題附圖截圖存入對應資料夾
  → 等待你通知「截圖完成，請開始解題」
    ↓
【你做】依提醒截圖存檔，完成後告知 Cowork
    ↓
【重要】Cowork 一次只解一題，解完存檔後再繼續下一題
    ↓
你加入補充截圖（chart/eqn/hand）
請 Cowork 更新 question_index.json（tags、verified）
    ↓
說：「ingest SD-XXXX-N」→ Cowork 直接執行，wiki 自動更新
```

---

## 兩個環境分工

| 環境 | 負責什麼 |
|------|---------|
| **你（使用者）** | PDF 題目附圖截圖（fig-N.png）、chart/eqn/hand 補充截圖、人工驗算後通知 Cowork 更新 verificationStatus |
| **Cowork** | 解題（SOLVE，**一次一題**）、存檔（.md + viz.html）、更新 question_index.json、**所有 wiki 操作指令**（ingest / compile-all / lint / status / reindex / add-concept / add-method / refresh-dashboard / frequency / analyze / predict / study / find / related / unverified / query，詳見 CLAUDE-CODE.md）、直接維護 wiki/diagnosis/ · wiki/failure-modes/ · wiki/materials/ · wiki/code-ref/ · wiki/queries/ · study/（study 指令輸出）、**修正 raw/solutions/methods/ 的公式錯誤**（須驗算＋同步 wiki＋記 log） |

---

## 單向資料流

```
raw/solutions/SD-XXXX-N/SD-XXXX-N.md  ──→  wiki/problems/      （Cowork: ingest）
raw/json/concepts.json                 ──→  wiki/concepts/      （Cowork: compile-all）
raw/solutions/methods/                 ──→  wiki/methods/       （Cowork: compile-all）
   ↑ 修正公式錯誤時改「這一端」，不要只改 wiki 副本（否則下次 compile 會被蓋回）
Cowork 查詢結果                        ──→  wiki/queries/       （Cowork 直接存入）
Cowork study 指令輸出                  ──→  study/              （Cowork 直接存入）
Cowork 跨層知識工具                    ──→  wiki/diagnosis/     （Cowork 直接存入）
                                       ──→  wiki/failure-modes/ （Cowork 直接存入）
                                       ──→  wiki/materials/     （Cowork 直接存入）
                                       ──→  wiki/code-ref/      （Cowork 直接存入）

解題內容唯一來源：raw/solutions/ 下的 .md 檔案
索引資訊唯一來源：raw/json/question_index.json
方法論唯一來源：raw/solutions/methods/（可修正，須驗算＋同步 wiki＋記 log，見規則 1）
wiki/queries/、study/（study 輸出）及四個跨層知識目錄：由 Cowork 直接寫入，不走 ingest 流程
```

---

## 資料夾結構

```
exam-wiki-SD/
├── README.md                        ← 冷啟動快速導覽
├── CLAUDE.md                        ← 本檔（身份層：分工、資料流、重要規則）
├── CLAUDE-SOLVE.md                  ← Cowork 解題 Skill
├── CLAUDE-CODE.md                   ← Cowork 操作指令（Runbook）
├── CLAUDE-SPEC.md                   ← 規格驗證層（格式、命名、完成標準）
│
├── study/                           ← 讀書筆記、講義、study 指令 HTML 輸出
│
├── raw/                             ← 所有原始資料（預設唯讀，僅 ✏️ 兩處可改）
│   ├── exams/                       ← 原始考卷 PDF（命名：SD-YYYY_結構動力分析與耐震設計.pdf）
│   ├── json/
│   │   ├── concepts.json            ← 概念定義（供 compile-all）
│   │   ├── syllabus_taxonomy.json   ← 命題大綱分類代號
│   │   └── question_index.json      ← ⭐✏️ 題目總索引（唯一需要人工維護的 JSON）
│   └── solutions/                   ← AI 解析 + 補充截圖（每題一個資料夾）
│       ├── SD-YYYY-N/               ← 🔒 證據，不可修改（規則 1、2）
│       │   ├── SD-YYYY-N.md
│       │   ├── SD-YYYY-N-fig-1.png
│       │   ├── SD-YYYY-N-[內容碼]-viz.html
│       │   └── *.pdf                ← 補充筆記（選用，命名無限制）
│       └── methods/                 ← ✏️ 解題方法論（可修正公式／單位，見規則 1）
│
└── wiki/                            ← 知識庫輸出
    ├── index.md                     ← 主導航（七層架構）
    ├── by-year.md                   ← 依考年分類
    ├── log.md                       ← 操作紀錄（append only）
    ├── concepts/                    ← 概念頁         ← Cowork (compile-all)
    ├── methods/                     ← 方法論頁       ← Cowork (compile-all)
    ├── traps/                       ← 陷阱頁         ← Cowork (compile-all)
    ├── problems/                    ← 題目頁         ← Cowork (ingest)
    ├── philosophy/                  ← 設計哲學頁     ← Cowork (compile-all)
    ├── queries/                     ← 查詢結果頁     ← Cowork (直接存入)
    ├── diagnosis/                   ← 題型診斷層     ← Cowork (直接存入)
    ├── failure-modes/               ← 失敗模式層     ← Cowork (直接存入)
    ├── materials/                   ← 材料行為層     ← Cowork (直接存入)
    └── code-ref/                    ← 規範條文對應層 ← Cowork (直接存入)
```

---

## 知識分類骨架（七層）

Wiki 導航依七層知識架構組織（前三層由 Cowork 透過 compile-all/ingest 生成，後四層由 Cowork 直接維護）：

| 層 | 目錄 | 維護者 | 內容 |
|----|------|:------:|------|
| Layer 1 | `concepts/` + `problems/` | Cowork (ingest/compile) | 核心動力學概念（自由度／振態／反應譜） |
| Layer 2 | `philosophy/` | Cowork (compile-all) | 耐震設計哲學與實務（性能設計／韌性容量設計） |
| Layer 3 | `methods/` | Cowork (compile-all) | 解題方法論（Duhamel 積分／模態疊加／靜力側推） |
| Layer 4 | `diagnosis/` | Cowork (直接存入) | 題型診斷決策樹 |
| Layer 5 | `failure-modes/` | Cowork (直接存入) | 失敗模式（軟弱層／短柱／扭轉不規則） |
| Layer 6 | `materials/` | Cowork (直接存入) | 材料與消能元件行為（阻尼器／隔震支承） |
| Layer 7 | `code-ref/` | Cowork (直接存入) | 規範條文對應（建築物耐震設計規範／橋梁耐震設計規範） |

---

## 命題大綱分類（依官方命題大綱）

> topicId 格式：`SD-Un-m`，U = 單元號，n = 子項號。
> `primaryTopicId` 填最主要考點；跨子項時用 `secondaryTopicIds` 列出。

| topicId | 命題大綱子項 |
|---------|------------|
| SD-U1-1 | 結構動力基本性質及原理 |
| SD-U1-2 | 運動方程式推導 |
| SD-U1-3 | 單自由度、多自由度系統之動態分析及應用 |
| SD-U2-1 | 地震力之設計規範 |
| SD-U2-2 | 建築耐震設計規範 |
| SD-U2-3 | 橋梁耐震設計規範 |
| SD-U3-1 | 結構耐震設計（含 RC 結構與鋼結構） |
| SD-U3-2 | 隔減震原理 |

> 完整代號定義見 `raw/json/syllabus_taxonomy.json`。

---

## 重要規則

1. **`raw/` 目錄下所有檔案一律不可修改**，僅以下兩處例外：
   - `raw/json/question_index.json`（索引唯一人工維護處）
   - `raw/solutions/methods/`（方法論文件，可修正公式錯誤與單位標註）

   > **為什麼 methods/ 是例外**：本規則要保護的是**證據**（考卷、AI 解析、驗證過的答案），
   > 這些一旦被改就失去可追溯性。但 `raw/solutions/methods/` 存的是**可維護的知識整理**，
   > 且它是 `wiki/methods/` 的 compile 來源 —— 只改 wiki 副本的話，下次 `compile-all` 會被蓋回舊版。
   > 發現公式或係數錯誤時，必須改 raw 來源才算根治。
   >
   > **修改 methods/ 的三個條件（缺一不可）**：
   > ① 修正前先做**數值驗算**（邊界代入、量綱檢查、與驗證解答交叉比對），不可憑印象改；
   > ② 改完**同步覆蓋** `wiki/methods/` 對應檔；
   > ③ 在 `wiki/log.md` 記錄**改了什麼、為什麼、怎麼驗證的**。
   >
   > ⚠️ `raw/solutions/SD-YYYY-N/`（個別題目解析）**不在例外內**，仍受規則 1 與規則 2 保護。

2. **`verifiedSolution` 是最終答案，不可質疑或重新計算**
3. **`wiki/log.md` 只可 append，不可刪除已有紀錄**
4. **wiki/ 大多數目錄是 compile 輸出，不可手動修改**；例外：diagnosis/ · failure-modes/ · materials/ · code-ref/ · queries/ 由 Cowork 直接維護
5. **ingest 前必須確認 verificationStatus = "verified"**
6. 概念連結使用 `[[concept_id]]`（Obsidian 相容）
7. 每次 ingest 同時更新 index.md 和 by-year.md
8. **格式與命名規範見 CLAUDE-SPEC.md；操作指令見 CLAUDE-CODE.md，全部由 Cowork 執行**

---

## 單位與符號慣例（本科特別容易出錯）

結構動力學橫跨數個單位制，且同一符號在不同章節意義不同，撰寫解析與方法論時務必標註：

| 項目 | 常見表示 | 注意 |
|------|---------|------|
| 質量 $m$ | tf·s²/cm、kg、N·s²/m | **重量 $W$ 與質量 $m$ 差一個 $g$**，本科最常見的錯 |
| 勁度 $k$ | tf/cm、kN/m | $k = cEI/L^3$ 的係數（3／12／48…）取決於邊界條件，不可套錯 |
| 圓頻率 $\omega$ | rad/s | 與頻率 $f$ (Hz) 差 $2\pi$；週期 $T = 2\pi/\omega$ |
| 阻尼比 $\xi$ | 無因次 | 題目給「5%」時代入 0.05，不是 5 |
| 反應譜加速度 $S_a$ | $g$ 的倍數 或 cm/s² | 以 $g$ 表示時要乘回 $g$ 才能與質量相乘得力 |

> **撰寫方法論頁與解析時，係數一律附上單位制標註，並盡量同時給出無因次形式。**
> （六科共同教訓：單位制錯配是知識庫最常累積的一類錯誤，見各科 log.md 的 FIX 紀錄。）

---

## CHANGELOG

| 日期 | 變更 | 原因 |
|------|------|------|
| 2026-07-25 | **重建 `CLAUDE.md` 與 `CLAUDE-CODE.md`**：原檔中文因編碼轉換損毀（常用字比例僅 15% / 6%，且含 `?` 表示位元已遺失、無法由 Big5/CP950 反解），以 exam-wiki-SS 的乾淨結構為模板重建；SD 專屬內容取自未受損來源（`wiki/index.md` 的 8 個單元名稱、`syllabus_taxonomy.json`、`question_index.json`、`README.md`）。舊檔保留為 `.bak` | 兩檔是 Cowork 每次 session 的必讀指令層，損毀等同無指令可循。其餘 99 份 raw 解析、140 頁 wiki 與另三個 harness 檔均完好 |
| 2026-07-25 | **修正科目代碼誤植**：損毀檔殘存英文顯示原本寫的是「RC（Reinforced Concrete Design and Prestress）」，應為 SD | 原檔係由 exam-wiki-RC 複製後未改科目識別，此錯誤被亂碼掩蓋 |
| 2026-07-25 | **規則 1 例外擴充**：`raw/` 唯讀的例外從「`question_index.json`」擴充為「`question_index.json` + `raw/solutions/methods/`」，並訂出三項修改條件（驗算／同步 wiki／記 log） | `methods/` 是 `wiki/methods/` 的 compile 來源，只改 wiki 副本會被 `compile-all` 蓋回；公式勘誤需能根治。個別題目解析仍受完整保護。六科統一 |
| 2026-08-09 | **新增 `study/problems-view/`（99 題渲染層）並重構五份 `study-SD-*.html` 為命題情報頁**：以 `unit-exam-intel` 產出六區塊（出題概況／考點結構／考點漂移／題型走向／考題清單／命題風險），數字全由 `stats.py` 自 `question_index.json` 算出、`verify.py` 對帳；刪除與 lecture／formula-given 重複的五個區段與互動測驗（經使用者確認）；題號連結由 `../index.html#md=` 改為 `problems-view/*.html` | 舊七區段頁與另兩份教材大量重複，且 KPI 有手打數字失準的風險；`#md=` 連結不會渲染公式與附圖 |

---

## 目前收錄狀況

> 此處不維護靜態數字（容易過時）。執行 `status` 指令可取得最新的驗證進度、解析題目數、標籤統計。
>
> 總題數：**99 題**（2002–2025 年，民國 91–114 年）
