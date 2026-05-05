import React from 'react';
import './Register.css';
import { useRegister } from '../hook/useRegister';

const Register: React.FC = () => {
    const { password, setPassword, rules, isPasswordValid, phone, handlePhoneChange } = useRegister();

    return (
        <div className="register-container">
            <div className="register-card">
                <h2 className="register-title">Cadastro</h2>

                <form>
                    <div className="form-group">
                        <label>Nome Completo</label>
                        <input type="text" className="form-input" maxLength={30} />
                    </div>

                    <div className="form-group">
                        <label>E-mail (@dominio.com)</label>
                        <input type="email" className="form-input" maxLength={20} />
                    </div>

                    <div className="form-group">
                        <label>Telefone</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="(00) 00000-0000"
                            value={phone}
                            onChange={handlePhoneChange}
                        />
                    </div>

                    <div className="form-group">
                        <label>Senha</label>
                        <input
                            type="password"
                            className="form-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <div className="validation-grid">
                            {Object.entries(rules).map(([key, met]) => (
                                <div key={key} className="rule-item" style={{ color: met ? '#16a34a' : '#9ca3af' }}>
                                    <div className="rule-dot" style={{ backgroundColor: met ? '#16a34a' : '#d1d5db' }} />
                                    <span>{key === 'length' ? '6-15 caracteres' :
                                        key === 'upper' ? 'Maiúscula' :
                                            key === 'lower' ? 'Minúscula' :
                                                key === 'number' ? 'Número' : 'Especial'}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button type="submit" className="btn-submit" disabled={!isPasswordValid}>
                        Finalizar Cadastro
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Register;