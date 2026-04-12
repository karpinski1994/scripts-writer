export interface HookSuggestion {
  hook_type: string;
  text: string;
  reasoning: string;
}

export interface HookAgentOutput {
  hooks: HookSuggestion[];
  confidence: number;
}

export interface NarrativePattern {
  pattern_name: string;
  description: string;
  structure: string[];
  fit_score?: number;
}

export interface NarrativeAgentOutput {
  patterns: NarrativePattern[];
  confidence: number;
}

export interface RetentionTechnique {
  technique_name: string;
  description: string;
  placement_hint: string;
}

export interface RetentionAgentOutput {
  techniques: RetentionTechnique[];
  confidence: number;
}

export interface CTASuggestion {
  cta_type: string;
  text: string;
  reasoning: string;
}

export interface CTAAgentOutput {
  ctas: CTASuggestion[];
  confidence: number;
}

export interface ScriptDraft {
  title: string;
  content: string;
  word_count: number;
  notes: string;
}

export interface WriterAgentOutput {
  script: ScriptDraft;
  confidence: number;
}

export interface ICPDemographics {
  age_range: string;
  gender: string;
  income_level: string;
  education: string;
  location: string;
  occupation: string;
}

export interface ICPPsychographics {
  values: string[];
  interests: string[];
  lifestyle: string;
  media_consumption: string[];
  personality_traits: string[];
}

export interface ICPProfile {
  demographics: ICPDemographics;
  psychographics: ICPPsychographics;
  pain_points: string[];
  desires: string[];
  objections: string[];
  language_style: string;
}

export interface ICPAgentOutput {
  icp: ICPProfile;
  confidence: number;
}
