# Exercise 2: Automate with your Agent Skill
Now that you saved your skill to Claude Cowork, you can invoke it in all of your future chats. 

## Exercise 2.1: evoke the agent skill via Claude Dispatch
Let's say you recieve a tenant's COI via email, but you're not currently at your computer. We can actually evoke our agent skills from dispatch. On your cellular phone with dispatch enabled, send one of the COI from the /coi folder and order claude to invoke your agent skill. 

## Exercise 2.2: evoke the agent skill on all the remaining COI using subagents
Evoke your skill (like `/YOUR-SKILL-NAME`) in Claude Cowork. In the `coi` folder of this directory, there are 9 additional COI to test the agent skill on. In your prompt, make sure to point Cowork to all the COIs. Instruct Cowork to put all the letters in the current directory. 

## Exercise 2.3: do a spot check
Your agent skill should return the following deficiencies: 

| Tenant | Coverage | Finding |
|---|---|---|
| Conflux Workspaces | Business Auto Liability | Coverage not provided on the certificate |
| Saltgrass Storage | Commercial Property (Special Form) | Coverage not provided on the certificate |
| Saltgrass Storage | Business Interruption / Extra Expense | Coverage not provided on the certificate |
| Summit Grid Analytics | Business Auto Liability | Coverage not provided on the certificate |
| Summit Grid Analytics | Business Interruption / Extra Expense | Coverage not provided on the certificate |
