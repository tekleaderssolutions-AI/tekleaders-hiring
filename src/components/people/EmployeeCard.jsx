import React from 'react';
import { Avatar } from '@/components/ui';
export default function EmployeeCard({ employee = {} }) {
  return (
    <div className="employee-card">
      <Avatar name={employee.name} size="lg" />
      <div className="employee-card-name">{employee.name}</div>
      <div className="employee-card-role">{employee.role}</div>
      <div className="employee-card-dept">{employee.department}</div>
    </div>
  );
}
