/**
 * @fileoverview Login page component for Montessori AI Agent application
 * Provides user authentication and onboarding experience
 */

import React, { useState } from 'react'
import styled from 'styled-components'
import { authService } from '../services/AuthService.js'

const LoginContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`

const LoginCard = styled.div`
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
  text-align: center;
`

const AppTitle = styled.h1`
  color: #667eea;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
`

const AppSubtitle = styled.p`
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
`

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

const Input = styled.input`
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`

const Select = styled.select`
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`

const SubmitButton = styled.button`
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 1rem;

  &:hover {
    background: #5a6fd8;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`

function LoginPage({ onLogin }) {
  const [formData, setFormData] = useState({
    childName: '',
    birthDate: '',
    caregiverType: 'parent'
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.childName || !formData.birthDate) {
      alert('Please fill in all required fields')
      return
    }

    setIsLoading(true)
    
    try {
      const profile = authService.login({
        name: formData.childName,
        birthDate: formData.birthDate,
        caregiverType: formData.caregiverType
      })
      
      onLogin(profile)
    } catch (error) {
      console.error('Login error:', error)
      alert('Failed to create profile. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <LoginContainer>
      <LoginCard>
        <AppTitle>Montessori AI Agent</AppTitle>
        <AppSubtitle>AI-Powered Child Development</AppSubtitle>
        
        <Form onSubmit={handleSubmit}>
          <Input
            type="text"
            name="childName"
            placeholder="Child's Name"
            value={formData.childName}
            onChange={handleInputChange}
            required
          />
          
          <Input
            type="date"
            name="birthDate"
            value={formData.birthDate}
            onChange={handleInputChange}
            required
          />
          
          <Select
            name="caregiverType"
            value={formData.caregiverType}
            onChange={handleInputChange}
          >
            <option value="parent">Parent</option>
            <option value="guardian">Guardian</option>
            <option value="teacher">Teacher</option>
            <option value="caregiver">Caregiver</option>
          </Select>
          
          <SubmitButton type="submit" disabled={isLoading}>
            {isLoading ? 'Creating Profile...' : 'Get Started'}
          </SubmitButton>
        </Form>
      </LoginCard>
    </LoginContainer>
  )
}

export default LoginPage