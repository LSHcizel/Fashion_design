export interface CriteriaScore {
  criteria: string;
  score: number;
  justification: string;
}

export interface DesignCase {
  id: string;
  name: string;
  imagePath: string;
  totalScore: number;
  scores: CriteriaScore[];
  strengths: string[];
  weaknesses: string[];
  improvements: string[];
}

export const designCases: DesignCase[] = [
  {
    id: "case-001",
    name: "Givenchy Black Tuxedo",
    imagePath: "fashion tuxedo elegant",
    totalScore: 42,
    scores: [
      {
        criteria: "Theme Relevance",
        score: 7,
        justification: "Accurate: The design interprets \"I Am Your Mirror\" through the literal reflectivity of the satin lapels and the conceptual idea of the black tuxedo as a \"social mirror\" or uniform. It shows a thoughtful understanding of the theme's essence but lacks the sublime depth that would redefine the concept."
      },
      {
        criteria: "Brand DNA Alignment",
        score: 8,
        justification: "Authentic / Orthodox: This look is quintessential Givenchy. It utilizes the brand's signature sharp, masculine-inspired tailoring and monochromatic \"dark romanticism\" palette. It remains relevant and contemporary while staying strictly within the established house codes."
      },
      {
        criteria: "Innovation & Originality",
        score: 5,
        justification: "Conservative: While the texture of the main fabric adds a subtle layer of interest, the silhouette and construction are safe and predictable. It follows established tuxedo trends without taking the avant-garde risks necessary to disrupt the category."
      },
      {
        criteria: "Aesthetics & Visual Impact",
        score: 7,
        justification: "Pleasing: The composition is harmonious, featuring a strong visual hierarchy centered on the deep V-neck and high-contrast lapels. It is an appealing, well-composed image with a clear aesthetic vision, though not quite \"stunning\" or breathtakingly unique."
      },
      {
        criteria: "Structural Logic & Material Expression",
        score: 8,
        justification: "Clear & Logical: The construction logic is sound, with the weight of the wool-blend body supporting the crisp lines of the satin lapels. The material behavior is technically sound and coherent, showcasing precise tailoring and realistic texture rendering."
      },
      {
        criteria: "Anticipated Functionality",
        score: 7,
        justification: "Comfortable: The garment appears to offer a well-balanced ergonomic fit. While the oversized shoulders suggest a slight restriction in extreme movement, it remains highly practical and comfortable for its intended formal-wear context."
      }
    ],
    strengths: [
      "Execution of Brand Codes: The design perfectly captures the Givenchy \"Aristocratic Noir\" aesthetic. The juxtaposition of matte and satin finishes is handled with professional restraint.",
      "Technical Precision: The structural integrity of the tailoring is impressive, presenting a sharp, authoritative silhouette that feels grounded and high-end.",
      "Thematic Coherence: Using formalwear as a \"mirror\" to reflect the wearer's identity is a clever, albeit safe, conceptual choice."
    ],
    weaknesses: [
      "Lack of Innovation: The design is remarkably traditional. For a prestigious house, one might expect a more disruptive take on the tuxedo—perhaps through deconstruction, unexpected material fusions, or a more radical interpretation of the \"Mirror\" theme.",
      "Predictability: The look feels like a \"core\" piece rather than a \"show\" piece, which may lack the emotional impact needed for a major collection launch."
    ],
    improvements: [
      "Enhance the Theme: To move into the \"Sublime\" range, consider incorporating actual reflective materials (mirrored shards, metallic threads) or asymmetrical elements to represent a \"broken\" or \"distorted\" mirror.",
      "Push the Silhouette: Experiment with the proportions of the lapels or the waist cinching to move away from conservative tailoring into a more evolutionary brand expression.",
      "Material Exploration: Integrating smart textiles or unconventional bonding techniques could elevate the innovation score while maintaining the structural logic."
    ]
  },
  {
    id: "case-002",
    name: "Avant-Garde Evening Gown",
    imagePath: "elegant evening gown haute couture",
    totalScore: 48,
    scores: [
      {
        criteria: "Theme Relevance",
        score: 9,
        justification: "Sublime: The design brilliantly captures the \"Metamorphosis\" theme through its transformative silhouette that evolves from structured bodice to fluid skirt, representing a butterfly emerging from its chrysalis."
      },
      {
        criteria: "Brand DNA Alignment",
        score: 8,
        justification: "Authentic: Maintains the house's commitment to feminine elegance while pushing boundaries with contemporary construction techniques."
      },
      {
        criteria: "Innovation & Originality",
        score: 8,
        justification: "Evolutionary: The integration of 3D-printed elements with traditional couture techniques represents a fresh approach to evening wear."
      },
      {
        criteria: "Aesthetics & Visual Impact",
        score: 9,
        justification: "Stunning: The gradient effect and architectural elements create a breathtaking visual statement that commands attention."
      },
      {
        criteria: "Structural Logic & Material Expression",
        score: 7,
        justification: "Clear: The construction demonstrates solid technical understanding, though the transition between rigid and soft materials could be more seamless."
      },
      {
        criteria: "Anticipated Functionality",
        score: 7,
        justification: "Comfortable: While visually dramatic, the design maintains wearability for formal occasions."
      }
    ],
    strengths: [
      "Exceptional Visual Impact: Creates an unforgettable presence on the runway.",
      "Innovative Material Use: Successfully blends traditional and modern techniques.",
      "Strong Thematic Expression: The metamorphosis concept is clearly communicated."
    ],
    weaknesses: [
      "Transition Refinement: The junction between structured and flowing elements needs refinement.",
      "Limited Versatility: The dramatic nature may limit wearing occasions."
    ],
    improvements: [
      "Soften Transitions: Use graduated materials to create a more organic flow between sections.",
      "Consider Modular Design: Allow removable elements to increase versatility.",
      "Enhance Comfort: Integrate hidden support structures for extended wear."
    ]
  },
  {
    id: "case-003",
    name: "Deconstructed Streetwear Jacket",
    imagePath: "urban streetwear jacket modern",
    totalScore: 39,
    scores: [
      {
        criteria: "Theme Relevance",
        score: 6,
        justification: "Appropriate: The \"Urban Chaos\" theme is present through asymmetric cuts and raw edges, but could be pushed further."
      },
      {
        criteria: "Brand DNA Alignment",
        score: 7,
        justification: "Authentic: Aligns well with the brand's streetwear heritage while introducing new elements."
      },
      {
        criteria: "Innovation & Originality",
        score: 6,
        justification: "Moderate: Deconstruction is a familiar approach in streetwear, though the execution is competent."
      },
      {
        criteria: "Aesthetics & Visual Impact",
        score: 7,
        justification: "Pleasing: Strong visual language that resonates with the target demographic."
      },
      {
        criteria: "Structural Logic & Material Expression",
        score: 6,
        justification: "Adequate: Some deconstructed elements feel arbitrary rather than purposeful."
      },
      {
        criteria: "Anticipated Functionality",
        score: 7,
        justification: "Comfortable: Maintains good functionality despite the deconstructed aesthetic."
      }
    ],
    strengths: [
      "Market Relevance: Strong appeal to the contemporary streetwear audience.",
      "Wearability: Successfully balances avant-garde aesthetics with practical use.",
      "Brand Consistency: Maintains recognizable brand elements."
    ],
    weaknesses: [
      "Originality: Similar approaches exist in the current market.",
      "Thematic Depth: The \"chaos\" concept could be expressed more boldly."
    ],
    improvements: [
      "Intensify Concept: Add unexpected material combinations or interactive elements.",
      "Enhance Uniqueness: Develop signature details that distinguish from competitors.",
      "Functional Innovation: Integrate technical features that enhance the urban lifestyle."
    ]
  },
  {
    id: "case-004",
    name: "Minimalist Wool Coat",
    imagePath: "minimalist coat elegant wool",
    totalScore: 44,
    scores: [
      {
        criteria: "Theme Relevance",
        score: 8,
        justification: "Accurate: Perfectly embodies the \"Essential Simplicity\" theme through refined reduction and focus on form."
      },
      {
        criteria: "Brand DNA Alignment",
        score: 9,
        justification: "Authentic: Quintessentially aligned with the brand's minimalist philosophy and attention to detail."
      },
      {
        criteria: "Innovation & Originality",
        score: 5,
        justification: "Conservative: While beautifully executed, the design plays it safe within minimalist conventions."
      },
      {
        criteria: "Aesthetics & Visual Impact",
        score: 8,
        justification: "Pleasing: Sophisticated and timeless appeal with excellent proportions."
      },
      {
        criteria: "Structural Logic & Material Expression",
        score: 9,
        justification: "Masterful: Exceptional understanding of material properties and construction techniques."
      },
      {
        criteria: "Anticipated Functionality",
        score: 8,
        justification: "Comfortable: Highly practical with excellent movement and versatility."
      }
    ],
    strengths: [
      "Technical Excellence: Superior construction quality and material selection.",
      "Timeless Design: Will remain relevant beyond seasonal trends.",
      "Brand Alignment: Perfect representation of house aesthetics."
    ],
    weaknesses: [
      "Limited Innovation: Doesn't push boundaries or introduce new ideas.",
      "Market Differentiation: May blend with competitor offerings."
    ],
    improvements: [
      "Subtle Innovation: Introduce hidden details or unexpected closures.",
      "Material Experimentation: Explore new wool treatments or blends.",
      "Signature Elements: Develop distinctive details that create brand recognition."
    ]
  },
  {
    id: "case-005",
    name: "Sustainable Tech Sportswear",
    imagePath: "athletic sportswear technical modern",
    totalScore: 51,
    scores: [
      {
        criteria: "Theme Relevance",
        score: 9,
        justification: "Sublime: Brilliantly interprets \"Future Sustainability\" by seamlessly merging eco-conscious materials with high-performance functionality."
      },
      {
        criteria: "Brand DNA Alignment",
        score: 8,
        justification: "Authentic: Advances the brand's commitment to innovation and sustainability while maintaining athletic heritage."
      },
      {
        criteria: "Innovation & Originality",
        score: 9,
        justification: "Disruptive: Introduces novel bio-based technical fabrics and pioneering construction methods."
      },
      {
        criteria: "Aesthetics & Visual Impact",
        score: 8,
        justification: "Pleasing: Clean, futuristic aesthetic that communicates performance and sustainability."
      },
      {
        criteria: "Structural Logic & Material Expression",
        score: 9,
        justification: "Masterful: Material choices perfectly support function with innovative seam-free construction."
      },
      {
        criteria: "Anticipated Functionality",
        score: 8,
        justification: "Comfortable: Excellent ergonomics with advanced moisture management and breathability."
      }
    ],
    strengths: [
      "Innovation Leadership: Sets new standards for sustainable performance wear.",
      "Technical Excellence: Superior functional performance across all metrics.",
      "Market Positioning: Addresses growing consumer demand for sustainable options."
    ],
    weaknesses: [
      "Production Scalability: New materials may face manufacturing challenges.",
      "Price Point: Innovation may result in higher costs affecting accessibility."
    ],
    improvements: [
      "Scalability Strategy: Develop partnerships to increase production capacity.",
      "Material Optimization: Continue research to reduce costs while maintaining performance.",
      "Consumer Education: Create campaigns explaining sustainability benefits."
    ]
  }
];

export const criteriaNames = [
  "Theme Relevance",
  "Brand DNA Alignment",
  "Innovation & Originality",
  "Aesthetics & Visual Impact",
  "Structural Logic & Material Expression",
  "Anticipated Functionality"
];

export interface ThemeAnalysisCriteria {
  category: string;
  criteria: string;
  score: number;
  justification: string;
}

export interface ThemeAnalysis {
  collectionName?: string;
  themeTitle: string;
  brand: string;
  analysisCriteria: ThemeAnalysisCriteria[];
  overallAssessment: {
    description: string;
    strengths: string[];
    weaknesses: string[];
    overallQuality: string;
  };
}

export const themeAnalysis: ThemeAnalysis = {
  themeTitle: "I Am Your Mirror",
  brand: "Givenchy",
  analysisCriteria: [
    {
      category: "Cohesion",
      criteria: "Narrative Cohesion",
      score: 9,
      justification: "Compelling Universe: The collection masterfully interprets the theme \"I Am Your Mirror\" through both literal and metaphorical lenses. It creates a complete narrative arc, moving from the sharp, dark reality of tailoring to the fractured, reflective world of the mirror-tile dress (Look 22) and the symbolic duality of the Yin-Yang cape (Look 21)."
    },
    {
      category: "Cohesion",
      criteria: "Visual Unity",
      score: 9,
      justification: "Seamless Unity: Every look is essential to the whole, tied together by a strict, sophisticated color story of midnight black, optic white, and liquid metallics. The repeated use of high-shine vinyl, satin lapels, and reflective surfaces ensures a consistent design language that is unmistakably cohesive."
    },
    {
      category: "Composition",
      criteria: "Range Balance",
      score: 8,
      justification: "Good Variety: The collection offers a well-rounded architecture, balancing high-drama couture pieces with versatile separates. It successfully covers diverse categories including sharp evening suiting, sculptural gowns, modern outerwear (Look 8, 11), and even luxurious knitwear (Look 24), providing a comprehensive wardrobe for the Givenchy client."
    },
    {
      category: "Composition",
      criteria: "Rhythm & Flow",
      score: 8,
      justification: "Dynamic Flow: There is an engaging progression of energy throughout the collection. The visual \"crescendo\" is effectively managed by alternating between matte textures and high-impact reflective materials, strategically placing statement pieces like the star-patterned bomber (Look 20) to maintain interest and pacing."
    }
  ],
  overallAssessment: {
    description: "The \"I Am Your Mirror\" collection for Givenchy is a sophisticated and highly polished body of work that perfectly aligns with the brand's heritage of \"Dark Romanticism\" and sharp Parisian tailoring.",
    strengths: [
      "Conceptual Depth: The translation of \"reflection\" into fabric—using mirror tiles, liquid-silver textiles, and high-gloss leather—is executed with technical brilliance.",
      "Aesthetic Consistency: The monochrome palette prevents the high-shine materials from feeling overwhelming, maintaining an air of classic luxury.",
      "Silhouette Mastery: The transition between hard, architectural shoulders and fluid, draped evening wear demonstrates a high level of design maturity."
    ],
    weaknesses: [
      "While the range is good, some of the more basic knitwear pieces (Look 12, 24) feel slightly detached from the high-octane energy of the mirror-themed statement looks, though they are necessary for commercial balance."
    ],
    overallQuality: "This is an exceptional collection that achieves a 9/10 level of cohesion. It succeeds in creating a \"Compelling Universe\" that feels both futuristic and grounded in couture traditions. The pacing ensures that the viewer is constantly engaged by new interpretations of the reflective theme without losing sight of the core brand identity."
  }
};
