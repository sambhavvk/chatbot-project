declare module "sentiment" {
  interface SentimentResult {
    score: number;
    comparative: number;
    tokens: string[];
    words: string[];
    positive: string[];
    negative: string[];
  }

  interface AnalysisOptions {
    extras?: Record<string, number>;
    language?: string;
    tokenizer?: (input: string) => string[];
  }

  class Sentiment {
    constructor(options?: AnalysisOptions);
    analyze(
      phrase: string,
      options?: AnalysisOptions
    ): SentimentResult;
  }

  export default Sentiment;
}