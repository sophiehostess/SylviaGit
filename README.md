# FX Trading and Pricing Library

A comprehensive Python library for FX (Foreign Exchange) trading, pricing, and risk calculations.

## Overview

This library provides tools and utilities for handling FX trades, including spot and forward trades, pricing calculations, PnL (Profit and Loss) analysis, and risk metrics like DV01 (Delta Value of 1 Basis Point).

## Core Components

### Trade Module
- FX trade creation and management
- Support for spot and forward trades
- Trade detail handling
- Multiple product types (spot, forward, NDF, time options)

### Rate Module
- Currency pair handling
- Market quotes
- Discount factors
- Capitalization factors
- Tenor management
- Quotation modes

### PnL Module
- Trade economic PnL
- PnL explanations
- Market data driven calculations

### PVBP/DV01 Module
- Zero curve DV01
- Forward trade sensitivities
- Bucket risk analysis

## Dependencies
- Python 3.x
- log4py (for logging)
- datetime (standard library)

## Testing
The library includes comprehensive unit tests covering:
- Trade creation and management
- Market quote curve construction
- Discount factor calculations
- PnL calculations
- Risk metrics (DV01)

Run tests using: 