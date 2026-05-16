import { useState, type FormEvent } from "react";
import { ArrowRight, LockKeyhole, ShieldCheck } from "lucide-react";
import { DEFAULT_LOGIN_CREDENTIALS } from "../lib/auth";
import type { SessionData } from "../types";

interface LoginScreenProps {
  onAuthenticated: (session: SessionData) => void;
}

export function LoginScreen({ onAuthenticated }: LoginScreenProps) {
  const [username, setUsername] = useState(DEFAULT_LOGIN_CREDENTIALS.username);
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (
      username.trim().toLowerCase() !== DEFAULT_LOGIN_CREDENTIALS.username ||
      password !== DEFAULT_LOGIN_CREDENTIALS.password
    ) {
      setErrorMessage("Credenciais inválidas para o usuário padrão do MVP.");
      return;
    }

    const session: SessionData = {
      username: DEFAULT_LOGIN_CREDENTIALS.username,
      displayName: DEFAULT_LOGIN_CREDENTIALS.displayName,
      role: DEFAULT_LOGIN_CREDENTIALS.role,
      accessToken: crypto.randomUUID(),
      authenticatedAt: new Date().toISOString(),
    };

    setErrorMessage(null);
    onAuthenticated(session);
  }

  return (
    <main className="login-screen">
      <section className="login-screen__hero">
        <div className="login-brand-mark">
          <ShieldCheck />
        </div>
        <h1>Keltech Document Management</h1>
        <p>
          Acesse a área operacional, acompanhe o pipeline de documentos e visualize os dados do upload em uma
          interface única.
        </p>
        <div className="login-screen__meta">
          <div>
            <strong>Login local</strong>
            <span>Autenticação simples para o MVP</span>
          </div>
          <div>
            <strong>SPA em React</strong>
            <span>Build estático servido pelo FastAPI</span>
          </div>
        </div>
      </section>

      <section className="login-screen__form-card">
        <div className="section-heading section-heading--login">
          <div>
            <h2>Entrar</h2>
            <p>Use o usuário padrão definido para este protótipo.</p>
          </div>
          <LockKeyhole className="section-heading__icon" />
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            <span>Usuário</span>
            <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="usuario@keltech.local" />
          </label>

          <label>
            <span>Senha</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Digite a senha local"
            />
          </label>

          {errorMessage ? <div className="feedback-box feedback-box--error">{errorMessage}</div> : null}

          <button className="primary-button" type="submit">
            Acessar dashboard
            <ArrowRight />
          </button>
        </form>
      </section>
    </main>
  );
}