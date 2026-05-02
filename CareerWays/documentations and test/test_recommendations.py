#!/usr/bin/env python3
"""
Test script for enhanced course recommendation system
"""

import requests
import json
import sys

def test_recommendation_system():
    """Test the enhanced recommendation system with sample inputs"""
    
    base_url = "http://localhost:5000/api/assessments"
    
    # Test cases with different user profiles
    test_cases = [
        {
            "name": "Software Developer wanting ML",
            "response": "I am a software developer with experience in Python and JavaScript. I want to learn machine learning and artificial intelligence to advance my career in tech. I have 3 years of experience building web applications and I'm passionate about creating innovative solutions.",
            "userType": "guest"
        },
        {
            "name": "Healthcare Professional",
            "response": "I'm a nurse with 5 years of experience in patient care. I want to transition into healthcare administration and management. I'm interested in learning about healthcare systems, leadership, and medical technology.",
            "userType": "guest"
        },
        {
            "name": "Business Student",
            "response": "I'm a business student studying marketing and finance. I want to learn digital marketing, data analysis, and business strategy to start my own company. I'm creative and love working with people.",
            "userType": "guest"
        }
    ]
    
    print("Testing Enhanced Course Recommendation System")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}/analyze",
                json={
                    "response": test_case["response"],
                    "userType": test_case["userType"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Analysis Status: {data.get('message', 'Success')}")
                print(f"Skills Found: {', '.join(data.get('skills', []))}")
                print(f"Interests: {', '.join(data.get('interests', []))}")
                print(f"Sentiment: {data.get('sentiment', 'N/A')}")
                
                # Check for enhanced features
                if 'embedding_data' in data:
                    print("Vector Embedding: Available")
                
                if 'recommendation_quality' in data:
                    quality = data['recommendation_quality']
                    print(f"Analysis Quality: {quality.get('relevant_matches', 0)} relevant courses from {quality.get('total_analyzed', 0)} analyzed")
                    print(f"Semantic AI: {'Enabled' if quality.get('uses_semantic_embedding') else 'Disabled'}")
                
                courses = data.get('courses', [])
                print(f"Recommended Courses: {len(courses)}")
                
                for j, course in enumerate(courses[:3], 1):
                    match_score = course.get('match_score', 0)
                    semantic_score = course.get('semantic_score', 0)
                    print(f"  {j}. {course.get('name', 'Unknown')} - {match_score:.1f}% match")
                    if semantic_score > 0:
                        print(f"     Semantic: {semantic_score:.1f}%")
                
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_recommendation_system()
