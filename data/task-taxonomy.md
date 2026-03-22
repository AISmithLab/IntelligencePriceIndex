# Task Taxonomy and Benchmark Mapping

**Created:** 2026-03-21
**Purpose:** Maps gig-economy task categories to AI benchmarks with historical score availability.

## Taxonomy Table

| # | Category | Example Tasks | Example Platforms | Candidate AI Benchmarks | Historical Data Available? |
|---|----------|--------------|-------------------|------------------------|---------------------------|
| T1 | **Writing & Content Creation** | Blog posts, SEO articles, copywriting, ghostwriting, product descriptions | Fiverr (Writing & Translation), Upwork (Content Writing, Sales & Marketing Copywriting) | AlpacaEval 2.0, MT-Bench, Chatbot Arena (writing subset), MMLU (language arts) | Yes -- AlpacaEval leaderboard (tatsu-lab GitHub); Chatbot Arena Elo history (LMSYS, 6M+ votes since May 2023); Epoch AI benchmark tracker |
| T2 | **Translation & Localization** | Document translation, website localization, subtitle translation, interpretation | Fiverr (Writing & Translation), Upwork (Translation & Localization Services) | WMT BLEU scores, FLORES-200, COMET | Yes -- WMT shared task results published annually since 2006 (statmt.org); NLP-progress tracker; Helsinki-NLP OPUS-MT leaderboard |
| T3 | **Coding & Software Development** | Web development, mobile apps, scripts, bug fixes, API integration, WordPress | Fiverr (Programming & Tech), Upwork (Web Development, Mobile Development, Desktop Application Development) | SWE-bench Verified/Pro, HumanEval(+), MBPP(+), BigCodeBench | Yes -- SWE-bench leaderboard (swebench.com); Epoch AI SWE-bench tracker; EvalPlus leaderboard (evalplus.github.io); scores from Jan 2023 onward |
| T4 | **Graphic Design & Illustration** | Logo design, brand identity, social media graphics, illustrations, infographics | Fiverr (Graphics & Design), Upwork (Branding & Logo Design, Graphic Design) | FID (MS-COCO), CLIP Score, CMMD, GenEval, DPG-Bench | Partial -- FID/CLIP scores reported in papers (DALL-E, Stable Diffusion, Midjourney); no single longitudinal leaderboard; Epoch AI tracks some image generation benchmarks |
| T5 | **Video & Animation** | Explainer videos, video editing, motion graphics, short-form video, animation | Fiverr (Video & Animation), Upwork (Video & Animation) | VBench, EvalCrafter, FVD (Frechet Video Distance) | Limited -- Video generation benchmarks are newer (2023+); VBench leaderboard on HuggingFace; historical depth is shallow |
| T6 | **Data Entry & Processing** | Data entry, data cleaning, spreadsheet management, web scraping, transcription | Fiverr (Business), Upwork (Data Entry & Transcription Services, Data Extraction/ETL) | GSM8K, MATH, TableQA benchmarks, Whisper WER (for transcription) | Yes -- GSM8K/MATH tracked on llm-stats.com and Epoch AI; Whisper WER improvements documented across model versions (V2 Dec 2022, V3 Nov 2023) |
| T7 | **Data Analysis & AI/ML** | Statistical analysis, data visualization, ML model building, AI integration | Fiverr (Programming & Tech), Upwork (Data Science & Analytics, AI & Machine Learning) | MATH, GSM8K-Platinum, MMLU (STEM), GPQA Diamond, Aider Polyglot | Yes -- MATH/MMLU/GPQA tracked on multiple leaderboards (llm-stats.com, Epoch AI, Scale Labs); historical scores from 2023 onward |
| T8 | **Digital Marketing & SEO** | SEO optimization, social media management, PPC campaigns, email marketing, content strategy | Fiverr (Digital Marketing), Upwork (Digital Marketing, Marketing PR & Brand Strategy) | MMLU (marketing/business), AlpacaEval (instruction following), Chatbot Arena | Partial -- General LLM benchmarks apply; no marketing-specific benchmark with longitudinal tracking |
| T9 | **Customer Service & Virtual Assistance** | Virtual assistant, customer support, chat support, email management, scheduling | Fiverr (Business), Upwork (Virtual Assistance, Customer Service & Tech Support) | Chatbot Arena Elo, MT-Bench, MMLU | Yes -- Chatbot Arena ratings tracked since May 2023 (6M+ votes); MT-Bench scores from June 2023 |
| T10 | **Legal & Professional Services** | Contract drafting, legal research, compliance review, tax preparation | Upwork (Corporate & Contract Law, Finance & Tax Law), Fiverr (Business) | LegalBench (162 tasks), MMLU (law/professional), LegalBenchmarks.ai | Partial -- LegalBench results available for major models; no long-running historical leaderboard; MMLU law subset tracked on standard leaderboards |
| T11 | **Audio & Music Production** | Voiceover, podcast editing, music composition, sound design, jingles | Fiverr (Music & Audio), Upwork (Audio & Music Production) | MusicCaps, AudioCaps, MOS (Mean Opinion Score) for TTS | Limited -- Audio generation benchmarks are fragmented; TTS quality improving but no unified longitudinal leaderboard |
| T12 | **Accounting & Business Consulting** | Bookkeeping, financial planning, business plans, market research, HR consulting | Upwork (Accounting & Consulting, Financial Planning), Fiverr (Business) | MMLU (accounting/finance), CFA-Bench, MATH | Partial -- MMLU finance subset tracked; CFA-style evaluations emerging but no deep historical series |

## Benchmark Availability Summary

| Benchmark | Type | Data Source | Historical Depth | Update Frequency |
|-----------|------|-------------|-----------------|------------------|
| SWE-bench Verified/Pro | Coding | swebench.com, Epoch AI | Aug 2024 -- present | Continuous (new submissions) |
| HumanEval(+) / MBPP(+) | Coding | evalplus.github.io | Jul 2021 -- present | Per model release |
| AlpacaEval 2.0 | Writing/instruction | tatsu-lab GitHub | Dec 2023 -- present | Per model release |
| MT-Bench | Conversation | LMSYS | Jun 2023 -- present | Per model release |
| Chatbot Arena Elo | General LLM | lmsys.org | May 2023 -- present (6M+ votes) | Continuous |
| WMT BLEU / COMET | Translation | statmt.org, NLP-progress | 2006 -- present (annual) | Annual shared task |
| FID / CLIP Score | Image generation | Paper-reported | ~2017 -- present | Per paper/model release |
| MMLU / MMLU-Pro | General knowledge | llm-stats.com, Epoch AI | 2020 -- present | Per model release |
| GPQA Diamond | Expert reasoning | llm-stats.com | 2023 -- present | Per model release |
| GSM8K / MATH | Math reasoning | llm-stats.com, Epoch AI | 2021 -- present | Per model release |
| LegalBench | Legal reasoning | legalbench.org | 2023 -- present | Per model release |
| Whisper WER | Speech recognition | OpenAI papers | 2022 -- present | Per model version |
| Epoch Capabilities Index | Composite | epoch.ai/benchmarks | 2012 -- present (37 benchmarks) | Continuous |

## Priority Categories for IPI

Based on (a) benchmark data depth, (b) platform task volume, and (c) documented AI displacement evidence, we prioritize:

1. **Tier 1 (strongest data):** Writing & Content (T1), Coding & Software Dev (T3), Graphic Design (T4), Translation (T2)
   - Rationale: Deep benchmark histories, high platform volume, empirical displacement evidence from Demirci et al. (2024) and Hui et al. (2023)

2. **Tier 2 (good data):** Data Entry & Processing (T6), Data Analysis (T7), Customer Service (T9)
   - Rationale: Strong general LLM benchmarks apply; Anthropic (2025) documents high exposure for customer service and data entry

3. **Tier 3 (emerging/partial):** Digital Marketing (T8), Legal (T10), Video & Animation (T5), Audio (T11), Accounting (T12)
   - Rationale: Benchmarks are newer, domain-specific, or fragmented; may require composite proxy measures

## Notes on Benchmark Selection Criteria

1. **Temporal coverage:** We prefer benchmarks with at least 2 years of historical scores to construct meaningful time series.
2. **Granularity:** Benchmarks that report individual model scores (not just SOTA) allow us to map capability improvements to specific time periods.
3. **Ecological validity:** Task-oriented benchmarks (SWE-bench, WMT) are preferred over knowledge-oriented benchmarks (MMLU) where available, as they better proxy real task performance.
4. **Composite indices:** The Epoch Capabilities Index (ECI) provides a fallback composite measure spanning 37 benchmarks, useful for categories lacking domain-specific benchmarks.
5. **Saturation risk:** Some benchmarks (e.g., GSM8K at ~96%, HumanEval at ~93%) are near saturation; we note harder variants (GSM8K-Platinum, HumanEval+, SWE-bench Pro) as alternatives.
