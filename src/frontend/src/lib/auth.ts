import type { UserRole } from "../types";

export const DEFAULT_LOGIN_CREDENTIALS = {
  username: "operador@keltech.local",
  password: "keltech123",
  displayName: "Operador Keltech",
  role: "operador" as UserRole,
};