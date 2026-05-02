"""
NLP and Machine Learning Engine for CareerWays
Handles text analysis, sentiment analysis, and recommendation engine
"""

import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
import string
import re
from collections import Counter
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using TF-IDF fallback.")


def ensure_nltk_resource(resource_path, download_name):
    """Download NLTK data only when missing."""
    try:
        nltk.data.find(resource_path)
    except LookupError:
        print(f"Downloading NLTK resource: {download_name}")
        try:
            nltk.download(download_name, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download {download_name}: {e}")


# Flag to track if NLTK resources have been initialized
_nltk_initialized = False


def _initialize_nltk_resources():
    """Initialize NLTK resources on first use (lazy loading)"""
    global _nltk_initialized
    if _nltk_initialized:
        return

    # Download required NLTK data
    ensure_nltk_resource('tokenizers/punkt', 'punkt')
    ensure_nltk_resource('corpora/stopwords', 'stopwords')
    ensure_nltk_resource('taggers/averaged_perceptron_tagger',
                         'averaged_perceptron_tagger')
    ensure_nltk_resource('chunkers/maxent_ne_chunker', 'maxent_ne_chunker')
    ensure_nltk_resource('corpora/words', 'words')

    _nltk_initialized = True


class NLPEngine:
    """Natural Language Processing Engine"""

    def __init__(self):
        # Initialize NLTK resources on first use
        _initialize_nltk_resources()

        self.stop_words = set(stopwords.words('english'))
        self.skill_keywords = {
            'programming': ['python', 'javascript', 'java', 'c++', 'coding', 'programming', 'sql', 'html', 'css'],
            'mathematics': ['math', 'calculus', 'algebra', 'statistics', 'numerical', 'computation'],
            'communication': ['writing', 'speaking', 'presentation', 'communication', 'leadership', 'teamwork'],
            'design': ['design', 'ui', 'ux', 'graphic', 'visual', 'creative', 'aesthetic'],
            'business': ['business', 'management', 'finance', 'accounting', 'economics', 'marketing', 'sales'],
            'healthcare': ['healthcare', 'medicine', 'nursing', 'medical', 'health', 'patient', 'care'],
            'education': ['teaching', 'education', 'learning', 'student', 'curriculum', 'pedagogy'],
            'science': ['science', 'research', 'biology', 'chemistry', 'physics', 'lab', 'experiment'],
            'technology': ['technology', 'software', 'hardware', 'network', 'cyber', 'ai', 'machine learning'],
            'arts': ['art', 'music', 'dance', 'theater', 'performance', 'creative', 'entertainment'],
            'hospitality': ['hospitality', 'hotel', 'tourism', 'travel', 'service', 'restaurant', 'customer'],
        }

    def tokenize(self, text):
        """Tokenize text into words and sentences"""
        sentences = sent_tokenize(text.lower())
        words = word_tokenize(text.lower())

        # Remove punctuation and stopwords
        filtered_words = [
            word for word in words
            if word not in self.stop_words and word not in string.punctuation
        ]

        return {
            'sentences': sentences,
            'words': filtered_words,
            'raw_words': words
        }

    def extract_sentiment(self, text):
        """Extract sentiment from text"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1

        # Classify sentiment
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': subjectivity
        }

    def extract_skills(self, text):
        """Extract skills from text using keyword matching, filtering out personal attributes"""
        text_lower = text.lower()
        identified_skills = []
        skill_categories = {}
        
        # Words to exclude (person, gender, profession, occupation descriptors)
        excluded_terms = {
            'person', 'people', 'individual', 'human', 'man', 'woman', 'male', 'female',
            'boy', 'girl', 'student', 'professional', 'worker', 'employee', 'employer',
            'teacher', 'nurse', 'doctor', 'engineer', 'manager', 'developer', 'programmer',
            'artist', 'designer', 'consultant', 'analyst', 'specialist', 'expert',
            'beginner', 'intermediate', 'advanced', 'novice', 'amateur', 'expert',
            'young', 'old', 'age', 'aged', 'years', 'year', 'old',
            'profession', 'occupation', 'job', 'career', 'work', 'position',
            'role', 'title', 'status', 'identity'
        }

        for category, keywords in self.skill_keywords.items():
            found_skills = []
            for keyword in keywords:
                if keyword in text_lower and keyword not in excluded_terms:
                    found_skills.append(keyword)

            if found_skills:
                skill_categories[category] = found_skills
                identified_skills.extend(found_skills)

        # Filter out any skills that are in the excluded list
        filtered_skills = [skill for skill in identified_skills if skill not in excluded_terms]

        return {
            'skills': list(set(filtered_skills)),
            'skill_categories': skill_categories,
            'skill_count': len(set(filtered_skills))
        }

    def extract_experiences(self, text):
        """Extract actual experiences (clubs, competitions, activities) from text"""
        text_lower = text.lower()
        sentences = sent_tokenize(text)
        
        # Experience keywords to look for
        experience_keywords = {
            'club': ['club', 'organization', 'society', 'association', 'group', 'membership'],
            'competition': ['competition', 'competed', 'contest', 'tournament', 'hackathon', 'olympiad', 'challenge'],
            'project': ['project', 'developed', 'created', 'built', 'implemented', 'designed'],
            'internship': ['internship', 'intern', 'training', 'apprenticeship', 'work experience'],
            'volunteer': ['volunteer', 'volunteering', 'community service', 'outreach', 'helped'],
            'leadership': ['leadership', 'led', 'managed', 'coordinated', 'organized', 'headed', 'captain', 'president', 'chair'],
            'research': ['research', 'studied', 'investigated', 'analyzed', 'experiment', 'thesis', 'dissertation'],
            'performance': ['performance', 'performed', 'concert', 'recital', 'show', 'exhibition', 'presentation'],
            'sports': ['sports', 'athletics', 'team', 'game', 'match', 'tournament', 'championship'],
            'creative': ['art', 'drawing', 'painting', 'writing', 'published', 'exhibition', 'portfolio'],
            'technical': ['coding', 'programming', 'developed software', 'built app', 'website', 'application'],
            'business': ['business', 'startup', 'entrepreneurship', 'marketing campaign', 'sales', 'finance project']
        }
        
        experiences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for exp_type, keywords in experience_keywords.items():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        # Extract the relevant phrase around the keyword
                        words = sentence_lower.split()
                        for i, word in enumerate(words):
                            if keyword in word:
                                # Get context (3 words before and after)
                                start = max(0, i - 3)
                                end = min(len(words), i + 4)
                                phrase = ' '.join(words[start:end])
                                # Capitalize first letter
                                phrase = phrase[0].upper() + phrase[1:] if phrase else phrase
                                if phrase not in experiences:
                                    experiences.append(phrase)
                                break
        
        return list(set(experiences))[:10]  # Return top 10 unique experiences

    def extract_entities(self, text):
        """Extract experience-related entities from text, not general nouns"""
        # Use the new experience extraction method
        experiences = self.extract_experiences(text)
        
        # If no experiences found, fallback to simple entity extraction but filter better
        if not experiences:
            sentences = sent_tokenize(text)
            entities = []
            
            # Experience-indicating words
            exp_indicators = ['joined', 'participated', 'attended', 'completed', 'achieved', 
                            'won', 'awarded', 'certified', 'trained', 'mentored', 'coordinated']
            
            for sentence in sentences:
                tokens = word_tokenize(sentence.lower())
                # Look for sentences with experience indicators
                if any(indicator in tokens for indicator in exp_indicators):
                    pos_tags = pos_tag(tokens)
                    for word, pos in pos_tags:
                        if pos in ['NN', 'NNP', 'NNS'] and len(word) > 3:
                            # Filter out personal/professional identity words
                            if word not in ['person', 'people', 'student', 'professional', 
                                          'worker', 'employee', 'teacher', 'doctor']:
                                entities.append(word)
            
            return list(set(entities))[:10]
        
        return experiences

    def extract_interests(self, text):
        """Extract interests and topics from text"""
        # Tokenize
        tokens_data = self.tokenize(text)
        words = tokens_data['words']

        # Get most common words as indicators of interest
        from collections import Counter
        word_freq = Counter(words)

        # Map to interest categories
        interests = set()
        text_lower = text.lower()

        interest_keywords = {
            'Technology': ['technology', 'software', 'computer', 'programming', 'coding', 'ai', 'data', 'tech'],
            'Business': ['business', 'management', 'entrepreneurship', 'finance', 'economics', 'leadership', 'marketing'],
            'Healthcare': ['healthcare', 'medicine', 'nursing', 'patient', 'health', 'medical', 'care'],
            'Education': ['education', 'teaching', 'learning', 'student', 'school', 'university', 'academic'],
            'Arts & Entertainment': ['art', 'music', 'entertainment', 'creative', 'design', 'media', 'performance'],
            'Science': ['science', 'research', 'biology', 'chemistry', 'physics', 'experiment', 'lab'],
            'Engineering': ['engineering', 'mechanical', 'electrical', 'civil', 'construction', 'infrastructure'],
            'Social Services': ['social', 'community', 'helping', 'people', 'nonprofit', 'counseling', 'welfare'],
            'Hospitality & Tourism': ['hospitality', 'tourism', 'travel', 'hotel', 'restaurant', 'service'],
        }

        for interest, keywords in interest_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                interests.add(interest)

        return list(interests) if interests else ['General Studies']

    def create_embedding(self, text):
        """Create vector embedding for text using sentence transformers or TF-IDF fallback"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                embedding = model.encode([text])[0]
                return embedding.tolist()
            except Exception as e:
                print(f"Sentence transformer error: {e}, falling back to TF-IDF")
        
        # Fallback to TF-IDF
        vectorizer = TfidfVectorizer(max_features=100)
        try:
            embedding = vectorizer.fit_transform([text]).toarray()[0]
            return embedding.tolist()
        except:
            return [0] * 100


class SentimentAnalyzer:
    """Advanced Sentiment Analysis"""

    @staticmethod
    def analyze(text):
        """Analyze sentiment in detail"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # More detailed sentiment analysis
        if polarity > 0.5:
            level = 'Very Positive'
        elif polarity > 0.1:
            level = 'Positive'
        elif polarity > -0.1:
            level = 'Neutral'
        elif polarity > -0.5:
            level = 'Negative'
        else:
            level = 'Very Negative'

        motivation_indicators = {
            'goal_oriented': any(word in text.lower() for word in ['goal', 'aim', 'want', 'achieve', 'accomplish']),
            'passionate': any(word in text.lower() for word in ['love', 'passionate', 'enjoy', 'excited', 'enthusiast']),
            'growth_mindset': any(word in text.lower() for word in ['learn', 'improve', 'grow', 'develop', 'challenge']),
            'experienced': any(word in text.lower() for word in ['experience', 'worked', 'project', 'internship', 'job']),
        }

        return {
            'polarity_score': polarity,
            'subjectivity_score': subjectivity,
            'sentiment_level': level,
            'motivation_indicators': motivation_indicators
        }


class RecommendationEngine:
    """Enhanced Course Recommendation Engine using Semantic Similarity"""

    def __init__(self, courses_data):
        """Initialize with courses data"""
        self.courses_data = courses_data
        self.vectorizer = TfidfVectorizer(max_features=200)
        self.course_embeddings = None
        self.semantic_embeddings = None
        self.use_semantic = SENTENCE_TRANSFORMERS_AVAILABLE
        self._prepare_embeddings()

    def _prepare_embeddings(self):
        """Prepare course embeddings using semantic models"""
        course_texts = []
        for course in self.courses_data:
            # Combine all text from course with better weighting
            text = f"{course.get('name', '')} {course.get('description', '')} {' '.join(course.get('skills_taught', []))} {' '.join(course.get('keywords', []))}"
            course_texts.append(text)

        # Prepare TF-IDF embeddings
        try:
            self.course_embeddings = self.vectorizer.fit_transform(course_texts)
        except:
            self.course_embeddings = None
        
        # Prepare semantic embeddings if available
        if self.use_semantic:
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                self.semantic_embeddings = model.encode(course_texts)
            except Exception as e:
                print(f"Semantic embedding preparation failed: {e}")
                self.semantic_embeddings = None
                self.use_semantic = False

    def recommend(self, user_text, top_n=5):
        """Recommend courses based on user text using enhanced semantic matching"""
        if self.course_embeddings is None and not self.use_semantic:
            return []

        similarities = np.zeros(len(self.courses_data))
        
        # Calculate semantic similarities if available
        if self.use_semantic and self.semantic_embeddings is not None:
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                user_embedding = model.encode([user_text])[0]
                semantic_similarities = cosine_similarity(
                    [user_embedding], self.semantic_embeddings)[0]
                similarities = semantic_similarities
            except Exception as e:
                print(f"Semantic similarity calculation failed: {e}")
                similarities = np.zeros(len(self.courses_data))
        
        # Calculate TF-IDF similarities as fallback or combination
        if self.course_embeddings is not None:
            try:
                user_embedding = self.vectorizer.transform([user_text])
                tfidf_similarities = cosine_similarity(
                    user_embedding, self.course_embeddings)[0]
                
                # Combine semantic and TF-IDF if both available
                if self.use_semantic and self.semantic_embeddings is not None:
                    similarities = 0.7 * similarities + 0.3 * tfidf_similarities
                else:
                    similarities = tfidf_similarities
            except Exception as e:
                print(f"TF-IDF similarity calculation failed: {e}")
        
        # Apply relevance filtering
        relevance_scores = self._calculate_relevance_scores(user_text)
        final_scores = similarities * relevance_scores
        
        # Get top N recommendations with minimum relevance threshold
        min_relevance_threshold = 0.1
        valid_indices = np.where(final_scores >= min_relevance_threshold)[0]
        
        if len(valid_indices) == 0:
            return []
        
        top_indices = valid_indices[np.argsort(final_scores[valid_indices])[::-1][:top_n]]

        recommendations = []
        for idx in top_indices:
            recommendations.append({
                'course_id': self.courses_data[idx].get('id'),
                'course_name': self.courses_data[idx].get('name'),
                'match_score': float(final_scores[idx]) * 100,
                'semantic_score': float(similarities[idx]) * 100 if self.use_semantic else None,
                'relevance_score': float(relevance_scores[idx]) * 100,
                'course_data': self.courses_data[idx]
            })

        return recommendations
    
    def _calculate_relevance_scores(self, user_text):
        """Calculate relevance scores based on keyword matching and semantic relevance"""
        user_text_lower = user_text.lower()
        user_tokens = set(re.findall(r'\b\w+\b', user_text_lower))
        relevance_scores = np.ones(len(self.courses_data))
        
        for i, course in enumerate(self.courses_data):
            course_text = f"{course.get('name', '')} {course.get('description', '')} {' '.join(course.get('skills_taught', []))} {' '.join(course.get('keywords', []))}".lower()
            course_tokens = set(re.findall(r'\b\w+\b', course_text))
            
            # Calculate token overlap
            overlap = len(user_tokens & course_tokens)
            union = len(user_tokens | course_tokens)
            jaccard_similarity = overlap / union if union > 0 else 0
            
            # Apply relevance boost for courses with meaningful overlap
            if jaccard_similarity > 0.05:
                relevance_scores[i] = 1.0 + jaccard_similarity * 2
            else:
                relevance_scores[i] = 0.5  # Penalty for low relevance
        
        return relevance_scores

    @staticmethod
    def calculate_match_score(user_skills, user_interests, course_skills, course_keywords):
        """Calculate enhanced match score with better weighting"""
        skill_match = 0
        interest_match = 0
        semantic_bonus = 0

        # Enhanced skill matching with partial credit
        if user_skills and course_skills:
            user_skills_set = set([skill.lower() for skill in user_skills])
            course_skills_set = set([skill.lower() for skill in course_skills])
            
            # Exact matches
            exact_matches = user_skills_set & course_skills_set
            skill_match = len(exact_matches) / max(len(course_skills), 1)
            
            # Partial matches (substring matching)
            partial_matches = 0
            for user_skill in user_skills_set:
                for course_skill in course_skills_set:
                    if user_skill in course_skill or course_skill in user_skill:
                        partial_matches += 0.5
                        break
            skill_match = min(1.0, skill_match + partial_matches / max(len(course_skills), 1))

        # Enhanced interest matching
        if user_interests and course_keywords:
            user_interests_set = set([interest.lower() for interest in user_interests])
            course_keywords_set = set([kw.lower() for kw in course_keywords])
            
            matching_interests = user_interests_set & course_keywords_set
            interest_match = len(matching_interests) / max(len(course_keywords), 1)
            
            # Semantic bonus for related interests
            related_interests = {
                'technology': ['programming', 'coding', 'software', 'computer', 'digital'],
                'business': ['management', 'finance', 'marketing', 'entrepreneurship', 'leadership'],
                'healthcare': ['medicine', 'nursing', 'medical', 'health', 'patient care'],
                'education': ['teaching', 'learning', 'academic', 'training', 'instruction']
            }
            
            for user_interest in user_interests_set:
                for category, related_terms in related_interests.items():
                    if user_interest in category:
                        for course_keyword in course_keywords_set:
                            if any(term in course_keyword for term in related_terms):
                                semantic_bonus += 0.1
                                break

        # Combined score with better weighting
        base_score = (skill_match * 0.5 + interest_match * 0.3 + semantic_bonus * 0.2) * 100
        overall_score = max(0, min(100, base_score))

        return {
            'overall_score': overall_score,
            'skill_match': skill_match * 100,
            'interest_match': interest_match * 100,
            'semantic_bonus': semantic_bonus * 100
        }


class RandomForestClassifier_Custom:
    """Custom Random Forest for course category classification"""

    def __init__(self):
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.categories = [
            'IT', 'Business', 'Healthcare', 'Education',
            'Engineering', 'Arts', 'Science', 'Hospitality'
        ]

    def classify(self, features):
        """Classify user profile into course categories"""
        # Features: [skill_count, sentiment_score, motivation_level, experience_level]
        try:
            prediction = self.clf.predict([features])[0]
            probabilities = self.clf.predict_proba([features])[0]

            return {
                'primary_category': self.categories[prediction],
                'category_probabilities': {
                    self.categories[i]: float(prob)
                    for i, prob in enumerate(probabilities)
                }
            }
        except:
            return {
                'primary_category': 'General Studies',
                'category_probabilities': {}
            }


# Initialize engines
nlp_engine = NLPEngine()
sentiment_analyzer = SentimentAnalyzer()
