// AI features
export enum AIFeatureType {
  RESUME_ANALYSIS = 'resume_analysis',
  RESUME_ENHANCEMENT = 'resume_enhancement',
  VACANCY_MATCHING = 'vacancy_matching',
  COVER_LETTER_GENERATION = 'cover_letter_generation',
  INTERVIEW_PREPARATION = 'interview_preparation',
  SKILL_GAP_ANALYSIS = 'skill_gap_analysis',
  CAREER_COACH = 'career_coach',
  JOB_RECOMMENDATIONS = 'job_recommendations',
}

// Resume analysis result
export interface ResumeAnalysis {
  id: string;
  userId: string;
  resumeUrl: string;
  analysis: {
    strengths: string[];
    weaknesses: string[];
    suggestions: string[];
    overallScore: number;
    keySkills: string[];
    experienceYears: number;
    educationLevel: string;
  };
  generatedAt: Date;
  expiresAt?: Date;
}

// Resume enhancement suggestion
export interface ResumeEnhancementSuggestion {
  id: string;
  userId: string;
  originalResume: string;
  enhancedResume: string;
  suggestions: {
    section: string;
    originalText: string;
    improvedText: string;
    reason: string;
  }[];
  appliedAt?: Date;
  createdAt: Date;
}

// Vacancy matching result
export interface VacancyMatchingResult {
  vacancyId: string;
  candidateId: string;
  matchScore: number; // 0-100
  matchDetails: {
    skillMatch: number;
    experienceMatch: number;
    educationMatch: number;
    locationMatch: number;
  };
  missingSkills: string[];
  matchingSkills: string[];
  explanation: string;
  generatedAt: Date;
}

// Cover letter generation
export interface CoverLetterGeneration {
  id: string;
  userId: string;
  vacancyId: string;
  coverletter: string;
  tone: 'professional' | 'friendly' | 'creative';
  generatedAt: Date;
  customizations?: {
    company: string;
    position: string;
    keyPoints: string[];
  };
}

// Interview preparation
export interface InterviewPreparation {
  id: string;
  userId: string;
  vacancyId: string;
  questions: InterviewQuestion[];
  tips: string[];
  estimatedDuration: number; // in minutes
  difficulty: 'easy' | 'medium' | 'hard';
  createdAt: Date;
}

// Interview question
export interface InterviewQuestion {
  id: string;
  question: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  suggestedAnswer: string;
  tips: string[];
}

// Skill gap analysis
export interface SkillGapAnalysis {
  id: string;
  userId: string;
  targetRole?: string;
  currentSkills: SkillLevel[];
  requiredSkills: SkillLevel[];
  gapSkills: SkillLevel[];
  recommendations: string[];
  estimatedLearningTime: number; // in hours
  resources: LearningResource[];
  createdAt: Date;
}

// Skill level
export interface SkillLevel {
  skill: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  yearsOfExperience?: number;
}

// Learning resource
export interface LearningResource {
  title: string;
  type: 'course' | 'tutorial' | 'documentation' | 'book';
  url?: string;
  estimatedTime: number; // in hours
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  provider?: string;
}

// Career coach conversation
export interface CareerCoachConversation {
  id: string;
  userId: string;
  messages: CareerCoachMessage[];
  topic: string;
  createdAt: Date;
  updatedAt: Date;
}

// Career coach message
export interface CareerCoachMessage {
  id: string;
  sender: 'user' | 'coach';
  content: string;
  timestamp: Date;
  context?: Record<string, any>;
}

// Job recommendations
export interface JobRecommendations {
  id: string;
  userId: string;
  recommendations: JobRecommendation[];
  generatedAt: Date;
  expiresAt?: Date;
}

// Job recommendation item
export interface JobRecommendation {
  vacancyId: string;
  matchScore: number;
  reasons: string[];
  skills: string[];
  gap: string[];
}

// AI usage statistics
export interface AIUsageStatistics {
  userId: string;
  featureUsage: Record<AIFeatureType, number>;
  totalRequests: number;
  creditUsage: number;
  period: {
    startDate: Date;
    endDate: Date;
  };
}