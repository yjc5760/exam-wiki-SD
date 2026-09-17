const { newPres, titleSlide, topicMapSlide, formulaSlide, flowchartSlide, flowMapSlide,
        diagramSlide, cheatSheetSlide, trapSlide, tableSlide, closingSlide } = require("./lib.js");

const pres = newPres();
const FOOT = "結構動力學「隔減震原理」觀念講義｜原理 · 公式 · 向量圖解";

/* 1 */
titleSlide(pres, {
  kicker: "SD-U3-2 · 結構動力｜觀念講義",
  title: "隔減震原理",
  subtitle: "隔震用「週期」把力打下來，用「阻尼」把位移收回來",
  tag: "全篇貫穿同一棟示範建築：W = 12,000 tf、八層、固定基礎 T = 0.80 s",
  footer: FOOT,
});

/* 2 */
topicMapSlide(pres, {
  eyebrow: "TOPIC MAP",
  title: "一個矛盾、一套手續、三條路線、一張檢查表",
  topics: [
    { title: "底層矛盾：力與位移", desc: "在反應譜的等速度段，Sa 與 T 成反比、D 與 T 成正比。週期延長 3 倍，力降為 1/3，位移卻漲 3 倍 —— 整個單元都在處理這個矛盾。" },
    { title: "通關手續：等效線性化", desc: "非線性元件一律換成「割線勁度 Keff ＋ 等效阻尼比 ξeq」。因為 Keff 是位移的函數，所以必須迭代。" },
    { title: "三條路線", desc: "① 隔震（LRB / FPS）動的是週期；② 消能（FVD / BRB）動的是阻尼、有時連勁度一起動；③ TMD 動的是共振。" },
    { title: "收尾：檢查數量級", desc: "Teff 約 2～4 s、隔震層位移約 15～40 cm、ξeq 約 15～30%。算完先量一次，再決定要不要相信自己的答案。" },
  ],
});

/* 3 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 底層邏輯",
  title: "隔震不是把結構做強，是把工作點搬到譜上力比較小的地方",
  diagram: "sd32-fig-1-two-knobs",
  insights: [
    "旋鈕①「延長週期」：沿 5% 設計譜往右走。本例 T 由 0.80 s 搬到 2.42 s，Sa 由 0.600 g 掉到 0.199 g。",
    "旋鈕②「提高阻尼」：整條譜垂直下壓 B1 倍。ξ = 23.3% 查得 B1 = 1.566，Sa 再降到 0.127 g。",
    "兩個旋鈕合起來：V/W 由 60% 降到 12.68%，基底剪力 7,200 → 1,521 tf，只剩 21%。",
    "注意順序：水平那段是隔震的本體，垂直那段只是阻尼的加分。只加阻尼不延長週期，效果差一個量級。",
  ],
  note: "本例的 60% 是「彈性需求」（未做韌性折減），用於前後對照；實際設計仍要依規範的韌性容量與結構系統折減。",
});

/* 4 */
formulaSlide(pres, {
  eyebrow: "FORMULA · 反應譜與阻尼折減",
  title: "為什麼延長週期一定會付位移的代價",
  formulas: [
    { label: "設計譜：等加速度段與等速度段", math: "f_sa" },
    { label: "由譜加速度回推譜位移 —— 等速度段 Sa ∝ 1/T，代進去得 D ∝ T", math: "f_sd" },
    { label: "阻尼比不是 5% 時，力與位移「同時」除以 B1", math: "f_b1" },
    { label: "有效振動週期（隔震題永遠是第一個算出來的量）", math: "f_teff" },
  ],
  note: "踩坑警訊：題目給的是總重 W 時，質量 m = W/g，千萬不能把 W 直接當質量代進根號裡 —— 本例 W = 12,000 tf 對應 m = 12.232 tf·s²/cm，差了 981 倍。",
});

/* 5 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 矛盾的全貌",
  title: "力往下、位移往上：阻尼是唯一能把代價收回來的東西",
  diagram: "sd32-fig-2-force-disp-tradeoff",
  insights: [
    "左圖：週期 0.80 → 2.42 s（3.0 倍），Sa 由 0.600 g 降到 0.199 g（約 1/3）—— 這是隔震的收益。",
    "右圖：同一段路，譜位移由 9.5 cm 漲到 28.8 cm —— 這是隔震的帳單，而且是隔震層一個人扛。",
    "阻尼 ξ = 23.3% 把 28.8 cm 壓回 18.4 cm，收回 36%。沒有這一步，隔震溝要做到 30 cm 以上。",
    "所以「隔震」與「消能」不是兩個可以二選一的方案，而是同一套系統裡互補的兩半。",
  ],
  note: "上部結構的層間變位則是相反方向：它從 9.5 cm 降到幾乎為零，因為變形全部集中到隔震層去了。",
});

/* 6 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 為什麼可以用單自由度",
  title: "隔震層與上部結構是「串聯」，最軟的彈簧主宰全局",
  diagram: "sd32-fig-3-series-spring",
  insights: [
    "串聯的意思是位移相加、力相同，所以是勁度的倒數相加：1/keq = 1/ksup + 1/kb。",
    "本例 kb/ksup = 0.109，隔震層軟了快 10 倍，keq = 74.4 tf/cm 只比 kb 小 10%。",
    "後果是第一振態幾乎是剛體平移，有效模態質量超過 95%，高振態可以忽略 —— 這才是等值靜力法合法的理由。",
    "誠實的但書：把上部結構當剛體算得 2.42 s，真正串聯是 2.55 s，位移會被低估約 5%。",
  ],
  note: "常見的觀念錯誤是把兩者的勁度直接相加（並聯）。並聯是「同一個位移、力相加」，隔震層與上部結構顯然不是這種關係。",
});

/* 7 */
formulaSlide(pres, {
  eyebrow: "FORMULA · 通關手續",
  title: "等效線性化：把非線性元件換成一根彈簧加一個阻尼比",
  formulas: [
    { label: "有效（割線）勁度 —— 必須通過原點與最大位移點", math: "f_keff" },
    { label: "等效阻尼比 —— 一圈遲滯面積除以彈性應變能", math: "f_xieq" },
    { label: "分母的彈性應變能一律用「系統」的割線勁度", math: "f_ws" },
    { label: "串聯關係：最軟的彈簧主宰整體", math: "f_series" },
  ],
  note: "三個最常見的分母錯誤：用切線勁度 kd、用單顆支承的勁度、用 1/2·k0·Dy²。分母錯了，阻尼比連帶 B1 全錯，力與位移一起偏掉。",
});

/* 8 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · LRB",
  title: "LRB 的一切都寫在這個迴圈裡：割線給勁度，面積給阻尼",
  diagram: "sd32-fig-4-bilinear-loop",
  insights: [
    "四個常數就決定整個元件：Qd = 600 tf（特徵強度）、k0 = 500、kd = 50 tf/cm、α = 0.1。",
    "由它們反推 Fy = Qd/(1−α) = 667 tf、Dy = Fy/k0 = 1.33 cm —— Dy 不是另外給的，是算出來的。",
    "割線 Keff = Qd/D + kd。D = 18.42 cm 時 Keff = 82.6 tf/cm，對應 Teff = 2.42 s。",
    "面積 WD = 4Qd(D − Dy) = 41,010 tf·cm。少扣 Dy 會把 WD 高估 8%，阻尼比跟著虛胖。",
  ],
  note: "迴圈右上角是沿 k0 卸載的，要走 2Dy = 2.67 cm 才回到另一條骨幹線 —— 這就是它是平行四邊形而不是矩形的原因。",
});

/* 9 */
formulaSlide(pres, {
  eyebrow: "FORMULA · LRB 鉛心橡膠支承",
  title: "雙線性模型：四個常數與兩條導出關係",
  formulas: [
    { label: "特徵強度與降伏位移（由 Fy、k0、α 互推）", math: "f_lrb_q" },
    { label: "骨幹曲線（降伏後）", math: "f_lrb_f" },
    { label: "有效勁度 —— 隨位移下降，所以必須迭代", math: "f_lrb_k" },
    { label: "一圈遲滯面積 —— 平行四邊形，務必扣掉 Dy", math: "f_lrb_w" },
  ],
  note: "Keff = Qd/D + kd 這條式子告訴你一件重要的事：位移愈大、Keff 愈小、週期愈長。所以大地震下隔震系統會「自動變軟」，這正是它保護上部結構的機制。",
});

/* 10 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 高頻掉分點",
  title: "取錯勁度，週期就整個跑掉",
  diagram: "sd32-fig-5-secant-vs-tangent",
  insights: [
    "割線 Keff = 82.6 tf/cm ⇒ T = 2.42 s，這是唯一正確的取法。",
    "誤取降伏後切線 kd = 50 ⇒ T = 3.11 s，偏長 29%：位移被高估、力被低估。",
    "誤取初始勁度 k0 = 500 ⇒ T = 0.98 s，偏短 59%：等於完全沒隔震到，力被大幅高估。",
    "判斷法只有一句話：割線必須同時通過「原點」與「本輪迭代的最大位移點」。",
  ],
  note: "等效線性化的整套理論建立在「同一個最大位移下，線性系統與非線性系統儲存相同的應變能」。這個條件只有割線滿足，切線不滿足。",
});

/* 11 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · FPS",
  title: "FPS：回復力來自幾何，阻尼來自摩擦，週期與重量無關",
  diagram: "sd32-fig-6-fps-geometry",
  insights: [
    "滑動面是半徑 R 的球面。滑塊偏離 D 時，重力分量提供回復力 W·D/R —— 純幾何，與材料無關。",
    "勁度 k = W/R 與質量 m = W/g 同時正比於 W，代進 T = 2π√(m/k) 之後 W 被約掉：T = 2π√(R/g)。",
    "本例 R = 220 cm ⇒ 單擺週期 2.98 s。建築加重、減重、改用途，這個週期都不會變。",
    "但含摩擦項的「有效週期」會隨位移改變：D = 15.45 cm 時 Teff = 2.19 s，兩者不是同一個東西。",
  ],
  note: "這個性質在實務上很值錢：質量估計誤差不會反映到隔震週期上，設計的不確定性比 LRB 低。代價是摩擦係數對溫度、速度與磨耗敏感。",
});

/* 12 */
formulaSlide(pres, {
  eyebrow: "FORMULA · FPS 摩擦單擺支承",
  title: "一個曲率半徑、一個摩擦係數，就全部決定了",
  formulas: [
    { label: "單擺週期 —— 與建築重量完全無關", math: "f_fps_t" },
    { label: "有效勁度 = 幾何回復項 ＋ 摩擦項", math: "f_fps_k" },
    { label: "一圈遲滯面積（Dy 趨近於零，所以不必扣）", math: "f_fps_w" },
    { label: "速算：最大傳遞力比與等效阻尼比", math: "f_fps_a" },
  ],
  note: "ξeq = 2μ/(πA) 是把 WD = 4μWD 與 Keff = W/R + μW/D 代進 ξ = WD/(2πKeffD²) 化簡的結果，不是另一條獨立公式。考場上忘了就現推，三行就出來。",
});

/* 13 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 統一觀點",
  title: "兩種支承其實共用同一條公式：WD = 4Q(D − Dy)",
  diagram: "sd32-fig-7-loop-compare",
  insights: [
    "LRB：Q 是鉛心的特徵強度 Qd = 600 tf，Dy = 1.33 cm 佔 D 的 7%，不可忽略。",
    "FPS：Q 是摩擦力 μW = 720 tf，起滑位移趨近於零，公式退化成 WD = 4μWD。",
    "所以「FPS 不用扣 Dy」不是特例，而是 Dy ≈ 0 的自然結果 —— 記一條公式就夠了。",
    "本例 WD 分別是 41,010 與 44,507 tf·cm，FPS 略高，因此阻尼比也較高（29.3% vs 23.3%）。",
  ],
  note: "分母一律用系統的割線勁度：ξ = WD/(2π·Keff·D²)。用單顆支承的勁度、或用 kd 當分母，都會算錯阻尼比。",
});

/* 14 */
tableSlide(pres, {
  eyebrow: "KNOWLEDGE CARD · 隔震選型",
  title: "LRB 與 FPS：拿到題目先看它動的是哪一組參數",
  header: ["項目", "LRB 鉛心橡膠支承", "FPS 摩擦單擺支承", "考場辨識關鍵字"],
  colW: [1.9, 3.7, 3.7, 2.8],
  rows: [
    ["物理機制",
     "橡膠提供回復力、鉛心剪切塑化消能",
     "球面重力提供回復力、滑動摩擦消能",
     "給 Qd / k0 / kd → LRB；給 R / μ → FPS"],
    ["週期",
     "T = 2π√(W/gKeff)，依賴重量",
     "T = 2π√(R/g)，與重量完全無關",
     "題目問「加重後週期如何變」"],
    ["有效勁度",
     "Keff = Qd/D + kd",
     "Keff = W/R + μW/D",
     "兩者都是 D 的函數 ⇒ 都要迭代"],
    ["遲滯面積",
     "WD = 4Qd(D − Dy)，Dy 必須扣",
     "WD = 4μWD，Dy ≈ 0 不必扣",
     "有沒有給 Dy 或 k0"],
    ["速算式",
     "—（老實代等效線性化）",
     "A = D/R + μ、ξe = 2μ/(πA)",
     "只給 R、μ、D 就是要你用速算"],
  ],
});

/* 15 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 阻尼折減",
  title: "B1 怎麼查、怎麼內插，以及為什麼不是 BS",
  diagram: "sd32-fig-9-b1-interp",
  insights: [
    "隔震後 Teff 落在 2～4 s，屬於長週期段，一律查 B1；BS 是短週期段用的。",
    "本例 LRB：ξ = 23.3%，在 20%（1.50）與 30%（1.70）之間線性內插得 B1 = 1.566。",
    "FPS：ξ = 29.3% ⇒ B1 = 1.687。摩擦型阻尼比高，折減也更大。",
    "同一個 ξ 若誤查 BS = 1.96，力會被低估 25% —— 這是整份考卷最容易被扣分的一個查表動作。",
  ],
  note: "力與位移必須用同一個 B1 折減。只折減其中一個，等於在同一張譜上用了兩種阻尼比。",
});

/* 16 */
formulaSlide(pres, {
  eyebrow: "FORMULA · 設計量與收斂",
  title: "算完 Keff 與 ξeq 之後，該產出什麼",
  formulas: [
    { label: "隔震層設計位移（折減後）", math: "f_b1" },
    { label: "基底剪力 —— 兩種算法必須相等，是很好的自我檢查", math: "f_v" },
    { label: "含扭轉的總設計位移（規範要求的最終檢核值）", math: "f_dtm" },
    { label: "收斂判準", math: "f_conv" },
  ],
  note: "Vb = Keff·D 與 Vb = W·Sa,eff 兩條路算出來必須一致（本例都是 1,521 tf）。若不一致，代表 Keff、D、B1 之中至少有一個沒有更新到同一輪。",
});

/* 17 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 為什麼要迭代",
  title: "迭代在找的是「代進去的位移」與「算出來的位移」相等的那一點",
  diagram: "sd32-fig-8-iteration",
  insights: [
    "Keff 是 D 的函數 ⇒ Teff 是 D 的函數 ⇒ Sa 是 D 的函數；ξeq 也是 D 的函數 ⇒ B1 也是。",
    "所以無法一次解出，只能猜一個 D 進去，看吐出來的 D 對不對得上 —— 這就是蛛網圖。",
    "曲線比 45° 線平緩，代表映射是收斂的；本例每輪誤差約縮小 3 倍。",
    "第 1 輪 20.0 → 19.0（誤差 5.2%），第 2 輪 19.0 → 18.6（誤差 1.8%），已進 5% 判準。",
  ],
  note: "考場上寫兩輪、附上收斂判準與誤差百分比，就是一份完整答案。只算一輪就交卷，第一輪的 20 cm 與定案差 9%，位移檢核會整個失真。",
});

/* 18 */
flowMapSlide(pres, {
  eyebrow: "SOLUTION FLOW",
  badge: "解",
  title: "示範建築配 LRB：求設計位移與基底剪力",
  subtitle: "W = 12,000 tf、初猜 20 cm，兩輪收斂",
  tag: "SD-U3-2",
  cols: 5,
  nodes: [
    { text: "初猜 D = 20 cm\nQd=600、kd=50", type: "start" },
    { text: "Keff = Qd/D + kd\n= 80.0 tf/cm", type: "step" },
    { text: "Teff = 2π√(W/gKeff)\n= 2.457 s", type: "step" },
    { text: "WD = 4Qd(D−Dy)\n= 44,800 tf·cm", type: "step" },
    { text: "ξ = WD/(2πKeffD²)\n= 22.3%", type: "step" },
    { text: "內插查表\nB1 = 1.546", type: "step" },
    { text: "D_new = gSaT²/4π²B1\n= 18.96 cm", type: "step" },
    { text: "誤差 5.2%\n大於 5%？", type: "decision" },
    { text: "第 2 輪：D = 18.96\n⇒ 18.61（誤差 1.8%）", type: "step" },
    { text: "收斂\nD = 18.4 cm", type: "step" },
  ],
  result: { text: "Vb = 1,521 tf\nV/W = 12.7%" },
  sideNote: {
    title: "初猜要怎麼猜",
    text: "用 D ≈ (g/4π²)·S_D1·T/B1 反算：假設 T ≈ 2.5 s、B1 ≈ 1.5，馬上得 20 cm 左右。猜得好可以少一輪，但猜得差也只是多算一輪，不影響最終答案。",
    color: "pink",
  },
  checklist: {
    title: "三個必做的驗證",
    items: [
      { label: "Keff 用割線", detail: "Qd/D + kd，不是 kd、也不是 k0" },
      { label: "WD 要扣 Dy", detail: "4Qd(D − Dy)，Dy = 1.33 cm" },
      { label: "兩條路算 Vb", detail: "Keff·D 與 W·Sa/B1 必須相等" },
    ],
  },
});

/* 19 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 結果對照",
  title: "同一棟建築：LRB 與 FPS 各自付出什麼、換到什麼",
  diagram: "sd32-fig-10-lrb-vs-fps",
  insights: [
    "基底剪力幾乎打平：LRB 12.68% vs FPS 13.02%，差不到 3%。",
    "位移差很多：LRB 18.4 cm、FPS 15.5 cm —— 因為 FPS 的摩擦阻尼比較高（29.3% vs 23.3%）。",
    "週期則相反：LRB 2.42 s 比 FPS 2.19 s 長，因為 FPS 的摩擦項把 Keff 撐高了。",
    "選型不是比誰的力小，而是比誰的位移、耐久性與造價在這個案子裡比較好接受。",
  ],
  note: "FPS 的摩擦係數對溫度與滑動速度敏感，規範通常要求用上下限兩組 μ 各算一次，取包絡。LRB 的鉛心性質相對穩定，但支承尺寸要做得更大。",
});

/* 20 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 消能減震",
  title: "速度型阻尼器與彈性力差 90°：不能把兩個峰值直接相加",
  diagram: "sd32-fig-11-fvd-phase",
  insights: [
    "阻尼力正比於速度，而速度與位移差 90°：最大位移時阻尼力恰為零，位移過零時阻尼力最大。",
    "這就是 FVD「只加阻尼、不加勁度」的物理根據 —— 它在結構變形最大的那一瞬完全不出力。",
    "合力峰值是向量和：√(1 + (2ξd)²) = 1.044，不是 1 + 0.30 = 1.30，直接相加會高估 25%。",
    "所以設計要分別檢核最大位移、最大速度、最大加速度三個狀態，再取包絡。",
  ],
  note: "斜撐角 θ = 30° 時，有效阻尼要乘 cos²θ = 0.75（力投影一次、位移投影一次）。本例要 C = 38.4 tf·s/cm 才換到 Δξ = 15%。",
});

/* 21 */
formulaSlide(pres, {
  eyebrow: "FORMULA · 速度型阻尼器",
  title: "黏滯阻尼器：出力、附加阻尼與斜撐投影",
  formulas: [
    { label: "阻尼器出力（β = 1 為線性黏滯）", math: "f_fvd" },
    { label: "斜撐投影：力投影一次、位移投影一次，故乘 cos²θ", math: "f_cos2" },
    { label: "附加阻尼比（單自由度、週期 T、勁度 k）", math: "f_dxi" },
    { label: "合力峰值是向量和，不是代數和", math: "f_phase" },
  ],
  note: "Δξ = πC·cos²θ/(Tk) 可以自己推：ξ = ceq/(2mω)，把 ceq = C·cos²θ、ω = 2π/T、m = kT²/4π² 代進去整理即得。記推導比記公式安全。",
});

/* 22 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 淨效益",
  title: "加了阻尼器不等於力一定變小：先看它有沒有同時改變勁度",
  diagram: "sd32-fig-12-brb-vs-fvd",
  insights: [
    "FVD 是垂直往下：週期不變 0.80 s，Sa 乾淨地被 B1 = 1.50 折減，力與位移同步降 33%。",
    "BRB 是先往左、再往下：加 50% 勁度使 T 縮到 0.65 s，5% 譜加速度反而由 0.600 g 漲到 0.735 g。",
    "BRB 的淨效益：力只少 9%（7,200 → 6,532 tf），位移卻少 40%（9.5 → 5.8 cm）。",
    "所以要控制層間變位選 BRB，要降低構件設計力選 FVD —— 兩者的用途本來就不同。",
  ],
  note: "若 T 縮短到落回等加速度平台段（本例 T0 = 0.6 s 以內），Sa 會停在 SDS 不再上升，這時 BRB 的淨效益判斷又要重來一次。這就是為什麼位移型一定要重新分析估算。",
});

/* 23 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · TMD",
  title: "TMD 的兩件事：調頻點反力抵消，再用阻尼把雙峰壓到等高",
  diagram: "sd32-fig-13-tmd-peaks",
  insights: [
    "機制一「反力抵消」：TMD 在調頻點反相振動，把外力抵掉。阻尼為零時抵消最乾淨，主結構位移趨近於零。",
    "代價是原本一個共振峰分裂成兩個無窮大的新峰 —— 所以純粹的無阻尼 TMD 不能用。",
    "機制二「阻尼消能」：加上 ξd 把雙峰壓下來。Den Hartog 最佳解讓兩峰等高，本例 √(1+2/μ) = 8.2。",
    "調頻目標是主結構原本的自然頻率，不是外力頻率 —— 這是最常被寫反的一句話。",
  ],
  note: "μ = 3% 的 TMD 折算成等效黏滯阻尼只有約 6%，遠不如隔震的 23%。而且地震是寬頻的，不保證落在調頻點上 —— TMD 的主戰場是風力與樓板舒適度，不是耐震。",
});

/* 24 */
formulaSlide(pres, {
  eyebrow: "FORMULA · TMD 調頻質量阻尼器",
  title: "Den Hartog 最佳解：質量比決定一切",
  formulas: [
    { label: "兩個無因次參數：質量比與頻率比", math: "f_tmd_m" },
    { label: "最佳調頻比 —— 注意 TMD 要調得比主結構稍「慢」一點", math: "f_tmd_f" },
    { label: "最佳阻尼比", math: "f_tmd_x" },
    { label: "最佳化之後的雙峰高度（用來估效益）", math: "f_tmd_p" },
  ],
  note: "本例 μ = 0.03：f_opt = 0.971、Td = 0.824 s、ξ_opt = 10.45%、雙峰 8.2、質量塊重 360 tf、行程約主結構位移的 4.8 倍。行程是 TMD 設計的真正瓶頸，屋頂要留得出那個空間。",
});

/* 25 */
flowchartSlide(pres, {
  eyebrow: "OVERVIEW · 考場作答流程",
  title: "隔減震題三步 SOP：先認裝置、再選路線、最後迭代收尾",
  stages: [
    { type: "step", text: "① 認裝置：題目給 Qd/k0/kd 就是 LRB；給 R/μ 就是 FPS；給 C 與斜撐角就是 FVD；給 md 與質量比就是 TMD" },
    {
      type: "decision", question: "它動的是哪一個旋鈕？",
      branches: [
        { label: "隔震", text: "動週期\n等效線性化\n＋必須迭代" },
        { label: "消能", text: "速度型只動阻尼\n位移型連勁度一起動\nT 要重算" },
        { label: "TMD", text: "動共振\nf_opt = 1/(1+μ)\n不必迭代" },
      ],
    },
    { type: "result", text: "算出 Keff、Teff、ξeq → 查 B1 → 回算 D → 檢查收斂 → 產出 D 與 Vb，最後用三把量級尺驗算" },
  ],
  note: "順序不能顛倒：認錯裝置就會代錯 WD 公式；沒認出「位移型會改變週期」就會漏掉 Sa 反而變大的那一步。",
});

/* 26 */
diagramSlide(pres, {
  eyebrow: "DIAGRAM · 收尾",
  title: "先看取捨地圖選對工具，再用三把尺檢查數量級",
  diagram: "sd32-fig-14-scheme-map",
  insights: [
    "取捨地圖：往左下走（力與位移同時變小）才是真的變好。隔震把力打到另一個量級，消能主要在收位移。",
    "尺一：有效週期 Teff 約 2～4 s。小於 1.2 s 表示隔震層太硬，大於 6 s 多半算錯。",
    "尺二：隔震層設計位移 D 約 15～40 cm。只有 5 cm 表示根本沒隔震到，超過 1 m 是公式代錯。",
    "尺三：等效阻尼比 ξeq 約 15～30%。LRB 落在 20～25%，FPS 含摩擦可以到 30%。",
  ],
  note: "這三把尺花不到十秒，卻能抓出絕大多數的代數與單位錯誤。答案寫完一定要回頭量一次。",
});

/* 27 */
cheatSheetSlide(pres, {
  eyebrow: "CHEAT SHEET · 考前速查（一）",
  title: "隔減震｜等效線性化與兩種隔震支承",
  cols: 3,
  items: [
    { label: "設計譜兩段", math: "f_sa" },
    { label: "譜位移 D ∝ T", math: "f_sd" },
    { label: "B1 折減（力與位移）", math: "f_b1" },
    { label: "割線勁度", math: "f_keff" },
    { label: "有效週期", math: "f_teff" },
    { label: "等效阻尼比", math: "f_xieq" },
    { label: "分母用系統勁度", math: "f_ws" },
    { label: "串聯彈簧", math: "f_series" },
    { label: "LRB：Qd 與 Dy", math: "f_lrb_q" },
    { label: "LRB：骨幹線", math: "f_lrb_f" },
    { label: "LRB：有效勁度", math: "f_lrb_k" },
    { label: "LRB：遲滯面積", math: "f_lrb_w" },
    { label: "FPS：單擺週期", math: "f_fps_t" },
    { label: "FPS：有效勁度", math: "f_fps_k" },
    { label: "FPS：遲滯面積", math: "f_fps_w" },
  ],
});

/* 28 */
cheatSheetSlide(pres, {
  eyebrow: "CHEAT SHEET · 考前速查（二）",
  title: "隔減震｜FPS 速算、設計量、消能與 TMD",
  cols: 3,
  items: [
    { label: "FPS 速算（A 與 ξe）", math: "f_fps_a" },
    { label: "基底剪力", math: "f_v" },
    { label: "含扭轉總位移", math: "f_dtm" },
    { label: "收斂判準", math: "f_conv" },
    { label: "FVD 出力", math: "f_fvd" },
    { label: "斜撐投影 cos²θ", math: "f_cos2" },
    { label: "FVD 附加阻尼", math: "f_dxi" },
    { label: "合力是向量和", math: "f_phase" },
    { label: "BRB 使週期縮短", math: "f_brb_k" },
    { label: "BRB 淨效益要重算", math: "f_brb_n" },
    { label: "TMD 兩個參數", math: "f_tmd_m" },
    { label: "TMD 最佳調頻比", math: "f_tmd_f" },
    { label: "TMD 最佳阻尼比", math: "f_tmd_x" },
    { label: "TMD 雙峰高度", math: "f_tmd_p" },
  ],
});

/* 29 */
trapSlide(pres, {
  eyebrow: "REVIEW",
  title: "高頻陷阱精選",
  traps: [
    { title: "把總重 W 當質量代進根號", desc: "T = 2π√(m/Keff) 的 m = W/g。本例 W = 12,000 tf 對應 m = 12.232 tf·s²/cm，忘記除以 g 會讓週期差 31 倍。" },
    { title: "Keff 取成切線勁度", desc: "等效線性化只認「過原點到最大位移」的割線。誤取 kd 週期偏長 29%，誤取 k0 偏短 59%，兩者都足以讓整題報銷。" },
    { title: "WD 忘了扣降伏位移 Dy", desc: "LRB 的迴圈是平行四邊形，WD = 4Qd(D − Dy)。本例 Dy = 1.33 cm，漏扣會把 WD 高估 8%、阻尼比虛胖。FPS 因 Dy ≈ 0 才不必扣。" },
    { title: "查成 BS 或只折減其中一個", desc: "隔震週期在長週期段，一律查 B1。ξ = 23.3% 時 B1 = 1.566、BS = 1.96，差 25%；而且力與位移必須用同一個 B1。" },
    { title: "只算一輪就把 D 當答案", desc: "Keff 與 ξeq 都是 D 的函數。本例初猜 20 cm 與定案 18.4 cm 差 9%，隔震溝與管線的位移檢核會整個失真。" },
    { title: "以為加阻尼器力一定變小", desc: "位移型（BRB）同時增加勁度，週期左移可能讓 Sa 反而變大。本例力只降 9%、位移卻降 40% —— 淨效益必須重新分析，不能想當然耳。" },
  ],
});

/* 30 */
closingSlide(pres, {
  title: "隔減震原理｜重點回顧",
  points: [
    "一句話：隔震用「週期」把力打下來，用「阻尼」把位移收回來 —— 兩件事互補，不是二選一。",
    "通關手續只有一套：割線 Keff、有效週期 Teff、等效阻尼比 ξeq = WD/(2π·Keff·D²)，然後迭代到收斂。",
    "LRB 與 FPS 共用 WD = 4Q(D − Dy)，差別只在 Q 是 Qd 還是 μW、Dy 大不大；FPS 的單擺週期與重量無關。",
    "消能要先問它動不動勁度：速度型只加阻尼、垂直往下；位移型連週期一起改，Sa 可能反而上升。",
    "TMD 靠調頻抵消加阻尼壓峰，對地震效益有限（μ = 3% 只折算到約 6% 阻尼），主戰場是風力與舒適度。",
    "收尾三把尺：Teff 約 2～4 s、D 約 15～40 cm、ξeq 約 15～30%。不合就回頭找單位或勁度的錯。",
  ],
});

pres.writeFile({ fileName: "SD-U3-2 隔減震原理.pptx" })
    .then(() => console.log("done"));
