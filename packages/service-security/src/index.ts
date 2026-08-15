import { timingSafeEqual } from "node:crypto";
import type { NextFunction, Request, Response } from "express";

function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required`);
  return value;
}

const token = required("INTERNAL_SERVICE_TOKEN");

export function requireInternal(request: Request, response: Response, next: NextFunction): void {
  const received = request.header("x-spas-internal-token");
  if (!received || received.length !== token.length || !timingSafeEqual(Buffer.from(received), Buffer.from(token))) {
    response.status(401).json({ error: "Unauthorized service request" });
    return;
  }
  next();
}
