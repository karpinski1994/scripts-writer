export interface ProviderConfig {
  name: string;
  api_key_masked: string;
  base_url: string;
  enabled: boolean;
  model: string;
}

export interface LLMSettings {
  providers: ProviderConfig[];
}

export interface ProviderStatus {
  name: string;
  reachable: boolean;
}

export interface LLMStatus {
  providers: ProviderStatus[];
}
