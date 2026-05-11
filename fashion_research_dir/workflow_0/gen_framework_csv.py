import csv

rows = [
    ['类别编号','类别名称（中）','类别名称（英）','关键点编号','关键点名称（英）','关键点名称（中）','评定问题','Givenchy SS2019 示例','Match条件','对标AlignEvaluator关键点'],

    # Cat.1
    ['Cat.1','服装品类与廓形','Garment Taxonomy & Silhouette','1','Garment Category','服装品类识别','文字是否正确命名服装品类？（连衣裙/风衣/西装/裤装/连体裤等）','Look01→连衣裙；Look05→风衣；Look40→双件套西装','品类名称与实物一致，不泛化为"上衣"等模糊词','Counting'],
    ['Cat.1','服装品类与廓形','Garment Taxonomy & Silhouette','2','Silhouette Archetype','廓形类型','是否描述服装整体廓形形态？（A字/H型/茧型/修身/廓形外套）','Look01→上紧下阔A字；Look35→宽松茧型长袍；Look45→修身直筒柱形','廓形描述与视觉形态匹配','Size'],
    ['Cat.1','服装品类与廓形','Garment Taxonomy & Silhouette','3','Hemline & Length','衣长与下摆线','是否准确描述衣长（及踝/midi/膝上）和下摆形态（平直/不对称/荷叶边）？','Look01→midi长不对称下摆；Look35→及踝拖地；Look25→全长不对称单袖','长度级别正确，下摆特殊形态有标注','Comparative Relation'],
    ['Cat.1','服装品类与廓形','Garment Taxonomy & Silhouette','4','Shoulder Architecture','肩部结构语言','是否描述肩线的设计形态？（夸张垫肩/自然肩/落肩/结构肩）','Look10/15/30均有强调肩线；Look25→单侧结构肩垫','肩部有特殊设计时必须描述，普通肩可略','Full-body Action（结构完整性）'],
    ['Cat.1','服装品类与廓形','Garment Taxonomy & Silhouette','5','Body Coverage Map','身体覆盖与裸露区域','是否描述哪些身体部位被遮盖/暴露？（露背/镂空腰/露肩/低领）','Look20→胸前大面积几何镂空；Look55→肩部链甲裸露；Look35→全身包裹无暴露','有特殊暴露/遮盖设计时必须描述','State'],

    # Cat.2
    ['Cat.2','面料质感与物性','Material Intelligence','6','Fabric Family','面料品类','是否正确识别主体面料品类？（皮革/绉缎/棉麻/针织/尼龙/链甲）','Look05→光面皮革；Look01/35→褶裥轻薄面料；Look55→链甲金属面料','面料描述与实际材质对应','Material'],
    ['Cat.2','面料质感与物性','Material Intelligence','7','Surface Finish','表面质感与光泽','是否描述面料表面效果？（高光漆皮/哑光/绒感/镭射/金属光泽）','Look05→高光漆皮感；Look50→哑光柔性布料','光泽感/质感描述与实物一致','Material（细分）'],
    ['Cat.2','面料质感与物性','Material Intelligence','8','Structural Weight','硬挺度与垂坠感','是否传达面料的支撑性或垂坠性？（挺括/飘逸垂坠/有型/柔软塌陷）','Look15→挺括硬质毛料套装；Look01→裙摆飘逸垂坠；Look35→宽松垂坠感袍装','特别明显的挺括或垂坠感需体现','Size（相对比较）'],
    ['Cat.2','面料质感与物性','Material Intelligence','9','Construction Technique','工艺手法识别','是否提及特殊面料工艺？（褶裥/绗缝/刺绣/贴花/激光切割/镂空/压花）','Look01→放射状褶裥；Look45→针织横肌拼接；Look50→花卉刺绣','有特殊工艺时需明确标注工艺名称','Hand Action（工艺细节）'],
    ['Cat.2','面料质感与物性','Material Intelligence','10','Material Hybrid Logic','多材质混搭逻辑','多材质时是否描述各材质的分布位置关系？','Look10→卡其棉夹克+皮领；Look45→针织绿色肩部+印花裙身；Look55→银色链甲叠在黑色面料上','多材质Look中各材质的位置关系须描述','Compositional Relation'],

    # Cat.3
    ['Cat.3','色彩系统与图案语言','Color System & Pattern Language','11','Primary Color Identity','主色调精准性','是否正确描述服装主色？（冰蓝灰/橄榄绿/钴蓝/玫瑰粉/全黑/锈色）','Look01→冰蓝灰；Look05→橄榄棕绿；Look30→钴蓝；Look35→玫瑰粉','避免泛化（"蓝色"不如"钴蓝"准确）','Expression（精准捕捉）'],
    ['Cat.3','色彩系统与图案语言','Color System & Pattern Language','12','Secondary Color & Proportion','副色及占比关系','存在显著副色时是否描述其颜色及大致视觉占比？','Look30→主钴蓝+副黑+点缀薄荷绿腰带；Look55→主黑+副银（约30%）','副色及视觉权重须体现','Cross-Entity Binding'],
    ['Cat.3','色彩系统与图案语言','Color System & Pattern Language','13','Color Relationship Logic','配色逻辑类型','是否描述配色方式？（单色/同类色/补色对比/撞色/渐变/黑白）','Look01→纯色单色；Look30→多色层次搭配；Look45→墨绿+黑色同类色对比','配色逻辑类型须能从描述中推断','Artistic Style（配色层面）'],
    ['Cat.3','色彩系统与图案语言','Color System & Pattern Language','14','Pattern Taxonomy','图案品类识别','是否正确识别图案种类？（无图案/几何/花卉/抽象/动物纹/格纹/条纹）','Look25→抽象散点菊花印花；Look45→对称辐射花卉；Look50→同心圆螺旋刺绣','图案描述与视觉类型匹配','Artistic Style（图案层面）'],
    ['Cat.3','色彩系统与图案语言','Color System & Pattern Language','15','Pattern Spatial Distribution','图案空间分布','是否描述图案在服装上的分布方式？（满版/局部/中心辐射/上重下轻/随机）','Look50→以胸口为中心向外辐射满版；Look25→上密下疏渐变分布','图案分布逻辑须与实物一致','Entity Layout'],
    ['Cat.3','色彩系统与图案语言','Color System & Pattern Language','16','Pattern Scale & Density','图案比例与密度','是否描述图案的大小比例（大花/小碎花）和密集度（密集/稀疏）？','Look25→小碎菊花密集；Look45→中等比例花卉疏密有致','特别明显的图案比例和密度须体现','Counting（图案数量层面）'],

    # Cat.4
    ['Cat.4','工艺与细节语言','Construction & Detail Language','17','Fastening & Closure','开合方式','是否描述服装的开合方式？（单/双排扣/隐形拉链/系带/搭扣）','Look05→双排扣；Look40→三粒单排扣；Look20→金属搭扣；Look55→宽扣腰带','有显著开合设计时须描述','Contact Interaction'],
    ['Cat.4','工艺与细节语言','Construction & Detail Language','18','Pocket & Functional Elements','口袋与功能性细节','是否提及口袋设计或功能性细节？（贴袋/插袋/工装口袋/D形环）','Look10/15→胸前贴袋；Look55→工装贴袋；Look15→裤腿挂带','口袋数量及位置须准确描述','State'],
    ['Cat.4','工艺与细节语言','Construction & Detail Language','19','Edge & Hem Treatment','边缘与下摆处理','是否描述边缘/下摆的特殊处理？（毛边/卷边/包边/流苏/荷叶边）','Look01→下摆不对称收边；Look15→腰部裤腿悬挂织带；Look25→不对称裁切边','非常规边缘处理须描述','State（设计状态）'],
    ['Cat.4','工艺与细节语言','Construction & Detail Language','20','Deconstruction & Subversion','解构与颠覆性细节','是否识别并描述打破常规的解构设计细节？','Look15→套装裤腿垂落装饰绑带；Look55→工装裤腿悬带；Look20→胸前结构性切割镂空','解构元素须明确标注，不能描述为普通设计','Counterfactual（打破常规）'],
    ['Cat.4','工艺与细节语言','Construction & Detail Language','21','Hardware & Embellishment','金属件与装饰元素','是否描述金属配件或装饰物？（链条/铆钉/金属环/水晶/亮片/链甲）','Look15→军绿D形金属环腰带；Look55→银色链甲织物；Look35→水晶宝石项链','有视觉冲击力的金属件/装饰须描述','Attribute Consistency'],

    # Cat.5
    ['Cat.5','配件与整体造型','Accessories & Total Styling','22','Bag Morphology','包袋形态描述','是否描述包袋的品类（clutch/托特/手拿）、形态和颜色材质？','Look20→黑白拼色硬壳几何袋；Look30→黑色菱形钻石形手拿包；Look40→深海军蓝品牌字样clutch','品类+形态+颜色三要素需覆盖','Containment Relation'],
    ['Cat.5','配件与整体造型','Accessories & Total Styling','23','Footwear Description','鞋履描述','是否描述鞋的品类（泵鞋/踝靴/长靴）、跟高、颜色和材质？','Look01→深蓝色低跟尖头泵鞋；Look20→黑色金属尖头高跟鞋；Look55→金色漆皮踝靴','跟高特征+颜色+鞋型三要素需覆盖','Expression'],
    ['Cat.5','配件与整体造型','Accessories & Total Styling','24','Jewelry & Ornament','首饰与身体装饰','是否描述首饰及装饰配件？（项链/耳饰/手镯/眼镜/头饰）','Look15→镶嵌水晶链条眼镜；Look35→多宝石垂坠项链；Look30/40→纤细银色颈链','有视觉突出的首饰时须描述品类和风格','Cross-Entity Binding'],
    ['Cat.5','配件与整体造型','Accessories & Total Styling','25','Belt & Waist Accent','腰带与腰部强调','是否描述腰带的宽度/材质/颜色/扣头形式及对腰部的塑形作用？','Look05→黑色宽皮腰带+大方扣；Look15→橄榄绿弹力腰带+D形扣；Look55→黑色多孔皮腰带','SS2019标志性元素，须单独描述','Attribute Consistency（集体约束）'],
    ['Cat.5','配件与整体造型','Accessories & Total Styling','26','Layering & Coordination','叠搭与穿搭逻辑','是否描述内外层搭配关系和上下装的穿搭逻辑？','Look10→卡其夹克+白T+黑裤三层次；Look30→蓝色连体裤+黑结构外套；Look55→链甲+黑马甲+黑工装裤三层','多件Look须描述穿搭主次关系','Compositional Relation'],

    # Cat.6
    ['Cat.6','空间比例与结构关系','Spatial & Proportional Structure','27','Top-to-Bottom Proportion','上下身比例关系','是否描述视觉重心的上下分布？（上宽下窄/上收下放/均衡/高腰/低腰）','Look01→上收下放；Look05→上重下轻；Look35→全身均衡宽松','视觉比例分布与描述一致','Comparative Relation'],
    ['Cat.6','空间比例与结构关系','Spatial & Proportional Structure','28','Volume Distribution','体量分布','是否描述服装各部位的体量感对比？（局部夸张膨胀/整体贴身/前后体量差）','Look25→肩部结构性堆叠体量+裙身流动；Look35→袖子宽大飘逸+裙身等量宽松','有明显体量对比时须描述','Size'],
    ['Cat.6','空间比例与结构关系','Spatial & Proportional Structure','29','Asymmetry Recognition','不对称性识别','是否识别并描述不对称设计元素？（单袖/不对称下摆/单侧装饰/错位拼接）','Look25→单袖+裸肩不对称设计；Look01→不对称裙摆收边','有不对称设计时须明确指出','Similarity Relation（镜像对称）'],
    ['Cat.6','空间比例与结构关系','Spatial & Proportional Structure','30','Cross-Garment Spatial Binding','跨单品空间属性绑定','整套Look中不同单品的空间属性是否被正确对应到各自单品，不混淆？','Look30→钴蓝=连体裤，黑色=外套，薄荷绿=腰带，三者属性须分别对应','多件单品各自属性不可混淆归属','Cross-Entity Binding'],

    # Cat.7
    ['Cat.7','概念与品牌基因','Conceptual & Brand DNA','31','Aesthetic Vocabulary','设计风格词汇','是否使用准确的风格关键词描述整体美学？（军装功能主义/解构优雅/极简结构）','SS2019核心：军装功能主义x高定结构感x雌雄同体电力美学','风格词汇能概括Look的核心美学基调','Artistic Style'],
    ['Cat.7','概念与品牌基因','Conceptual & Brand DNA','32','Cultural & Historical Reference','文化/历史引用','是否描述明显的文化或历史设计参照？（军装/哥特/东方袍服/中世纪链甲）','Look05/15→军装（Military）；Look35→东方袍服（Caftan）；Look55→中世纪链甲（Chainmail）','有清晰历史参照时须描述来源','World Knowledge'],
    ['Cat.7','概念与品牌基因','Conceptual & Brand DNA','33','Gender Expression','性别气质表达','是否描述服装的性别气质方向？（阳刚/柔美/雌雄同体/中性/跨性别编码）','Look15→女性穿正装男性廓形套装（雌雄同体）；Look35→极度柔美玫瑰粉袍','有明显性别张力时须描述','World Knowledge（文化认知层面）'],
    ['Cat.7','概念与品牌基因','Conceptual & Brand DNA','34','Thematic Narrative','主题叙事一致性','描述是否体现系列主题相关的叙事元素？（镜像/对称/反射/重复/双重性）','Look45→对称辐射印花（镜像感）；Look50→同心圆辐射（镜面涟漪）；Look01→褶裥重复反射','系列主题元素须在描述中有所体现','Counterfactual（打破常规叙事）'],
    ['Cat.7','概念与品牌基因','Conceptual & Brand DNA','35','Brand Heritage Alignment','品牌传承语言符合度','描述是否体现Givenchy的品牌设计基因？（结构廓形/军装改造/黑色基调/贵族简洁）','品牌语言：结构性肩线/军装功能元素/优雅简洁黑色系/精密缝制感','须体现至少一个品牌识别元素','Knowledge Application'],

    # Cat.8
    ['Cat.8','语义精准与语法','Semantic Precision & Grammar','36','Negation & Absence','否定与缺省描述','是否正确描述"没有"的设计元素？（无领/无装饰/无图案/无袖/无腰带）','Look35→无任何图案纯色；Look01→无配饰首饰；Look45→无腰带（腰部无收紧处理）','有意识的"缺省"设计须在描述中体现','Negation'],
    ['Cat.8','语义精准与语法','Semantic Precision & Grammar','37','Quantity Accuracy','数量准确性','是否准确描述数量信息？（扣子数量/口袋数量/层次数量/悬带数量）','Look05→双排各3粒扣（共6粒）；Look55→腰带4孔眼设计；Look15→裤侧面垂落3条织带','数量信息与实物一致（数量>=3时重点检验）','Counting (n>=3)'],
    ['Cat.8','语义精准与语法','Semantic Precision & Grammar','38','Pronoun & Reference Clarity','代词与指代清晰度','描述中的代词是否清晰指向正确的单品或部位，不产生歧义？','多件单品描述中"它的领口"须明确指向某一具体单品，不可歧义','多件单品的描述中不得出现指代不清','Pronoun Resolution'],
    ['Cat.8','语义精准与语法','Semantic Precision & Grammar','39','Attribute-Entity Binding Accuracy','属性-实体绑定精准度','每个属性是否正确绑定到对应的单品/部位，不发生属性张冠李戴？','Look30→薄荷绿=腰带（非连体裤），黑色=外套（非连体裤），钴蓝=连体裤','属性须准确绑定到对应实体，不可混淆','Attribute Consistency / Cross-Entity Binding'],
    ['Cat.8','语义精准与语法','Semantic Precision & Grammar','40','Over/Under-specification','过度描述与欠描述检测','描述是否在核心信息上缺失（欠描述），或对无关细节过度展开导致重心偏移（过度描述）？','欠描述例：仅说"一件黑色上衣"；过度描述例：大篇幅描述T台背景光线而忽略服装本身','核心设计信息覆盖率>=70%；无关描述占比<=20%','Text Layout（信息排布）'],
]

output_path = r'E:\fashion_agents_project\fashion_research_dir\workflow_0\fashion_eval_framework_40kp.csv'
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print('CSV saved:', output_path)
print('Total rows (excluding header):', len(rows)-1)
