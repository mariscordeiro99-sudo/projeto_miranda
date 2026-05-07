import { useState } from 'react';
import type { PasswordRules } from '../types/password';

export const useRegister = () => {
    const [password, setPassword] = useState('');
    const [phone, setPhone] = useState('');

    const rules: PasswordRules = {
        length: password.length >= 6 && password.length <= 15,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password)
    };

    const isPasswordValid = Object.values(rules).every(Boolean);

    const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 11) value = value.slice(0, 11);

        value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
        value = value.replace(/(\d{5})(\d)/, '$1-$2');

        setPhone(value);
    };

    return {
        password,
        setPassword,
        rules,
        isPasswordValid,
        phone,
        handlePhoneChange
    };
};