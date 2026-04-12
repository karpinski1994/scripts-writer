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

export interface ICPProfileResponse {
  id: string;
  project_id: string;
  demographics: ICPDemographics;
  psychographics: ICPPsychographics;
  pain_points: string[];
  desires: string[];
  objections: string[];
  language_style: string;
  source: string;
  approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface ICPUpdateRequest {
  demographics?: ICPDemographics | null;
  psychographics?: ICPPsychographics | null;
  pain_points?: string[] | null;
  desires?: string[] | null;
  objections?: string[] | null;
  language_style?: string | null;
  approved?: boolean | null;
}
