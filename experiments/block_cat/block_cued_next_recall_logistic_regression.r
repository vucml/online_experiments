#!/usr/bin/env Rscript

# ----------------------------------------------------------
# Analysis script: Block‐Cued Next Recall Logistic Regression
# ----------------------------------------------------------

# 1. Load required packages
library(dplyr)
library(car)

# 2. Read the data
df <- read.csv("experiments/block_cat/block_test.csv",
               stringsAsFactors = FALSE)

# 3. Prepare the data
df <- df %>%
  mutate(
    # Recency covariate for a 15‑item list
    DistFromEnd = 16 - CandPos,
    # Convert "TRUE"/"FALSE" (any case) into 1/0
    Chosen  = as.integer(tolower(Chosen)  == "true"),
    SameCat = as.integer(tolower(SameCat) == "true")
  )

# 4. Fit the fixed‑effects logistic regression
#    Predictors: AbsLag (temporal adjacency), SameCat (semantic),
#                DistFromEnd (recency bias)
model_glm <- glm(
  formula = Chosen ~ AbsLag + SameCat + DistFromEnd,
  data    = df,
  family  = binomial(link = "logit")
)

# 5. Summarize model results
cat("\n--- Logistic Regression Results ---\n")
print(summary(model_glm))

# 6. Check multicollinearity with Variance Inflation Factors
cat("\n--- Variance Inflation Factors (VIF) ---\n")
print(vif(model_glm))
