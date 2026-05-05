import { useState } from 'react';

export const useAuth = () => {
  const [password, setPassword] = useState('');
  const [loginId, setLoginId] = useState('');

  const applyPhoneMask = (value: string) => {
    let val = value.replace(/\D/g, '');
    if (val.length > 11) val = val.slice(0, 11);
    val = val.replace(/^(\d{2})(\d)/g, '($1) $2');
    val = val.replace(/(\d{5})(\d)/, '$1-$2');
    return val;
  };

  const handleLoginIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (!value.includes('@') && /\d/.test(value)) {
      setLoginId(applyPhoneMask(value));
    } else {
      setLoginId(value);
    }
  };

  return {
    password,
    setPassword,
    loginId,
    handleLoginIdChange
  };
};