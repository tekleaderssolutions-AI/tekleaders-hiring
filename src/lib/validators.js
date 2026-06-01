import * as yup from 'yup';

export const loginSchema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'At least 6 characters').required('Password is required'),
});

export const signupSchema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(8, 'At least 8 characters').required('Password is required'),
  confirmPassword: yup.string()
    .oneOf([yup.ref('password')], 'Passwords must match')
    .required('Confirm your password'),
});

export const jobSchema = yup.object({
  title: yup.string().required('Job title is required').min(3),
  department: yup.string().required('Department is required'),
  location: yup.string().required('Location is required'),
  type: yup.string().oneOf(['full-time', 'part-time', 'contract', 'internship']).required(),
  description: yup.string().required('Description is required').min(50),
});

export const candidateSchema = yup.object({
  firstName: yup.string().required('First name is required'),
  lastName: yup.string().required('Last name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  phone: yup.string(),
  resumeUrl: yup.string().url('Invalid URL'),
});
