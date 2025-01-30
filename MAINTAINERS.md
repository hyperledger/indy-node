# Maintainers

## Maintainer Scopes, GitHub Roles and GitHub Teams

The Maintainers of this repo, defined as GitHub users with escalated privileges
in the repo, are managed in the Hyperledger "governance" repo's [access control file](https://github.com/hyperledger/governance/blob/main/access-control.yaml). Consult that to see:

- What teams have escalated privileges to this repository.
- What GitHub roles those teams have in the repository.
- Who are the members of each of those teams.

The actions covered below for [becoming](#becoming-a-maintainer) and [removing](#removing-maintainers) are made manifest through PRs to that file.

## The Duties of a Maintainer

Maintainers are expected to perform the following duties for this repository. The duties are listed in more or less priority order:

- Review, respond, and act on any security vulnerabilities reported against the repository.
- Review, provide feedback on, and merge or reject GitHub Pull Requests from
  Contributors.
- Review, triage, comment on, and close GitHub Issues
  submitted by Contributors.
- When appropriate, lead/facilitate architectural discussions in the community.
- When appropriate, lead/facilitate the creation of a product roadmap.
- Create, clarify, and label issues to be worked on by Contributors.
- Ensure that there is a well defined (and ideally automated) product test and
  release pipeline, including the publication of release artifacts.
- When appropriate, execute the product release process.
- Maintain the repository CONTRIBUTING.md file and getting started documents to
  give guidance and encouragement to those wanting to contribute to the product, and those wanting to become maintainers.
- Contribute to the product via GitHub Pull Requests.
- Monitor requests from the Hyperledger Technical Oversight Committee about the
contents and management of Hyperledger repositories, such as branch handling,
required files in repositories and so on.
- Contribute to the Hyperledger Project's Quarterly Report.

## Becoming a Maintainer

This community welcomes contributions. Interested contributors are encouraged to
progress to become maintainers. To become a maintainer the following steps
occur, roughly in order.

- The proposed maintainer establishes their reputation in the community,
  including authoring five (5) significant merged pull requests, and expresses
  an interest in becoming a maintainer for the repository.
- An issue is created to add the proposed maintainer to the list of active maintainers.
- The issue is authored by an existing maintainer or has a comment on the PR from an existing maintainer supporting the proposal.
- The issue is authored by the proposed maintainer or has a comment on the issue from the proposed maintainer confirming their interest in being a maintainer.
  - The issue or comment from the proposed maintainer must include their
    willingness to be a long-term (more than 6 month) maintainer.
- Once the issue and necessary comments have been received, an approval timeframe begins.
- The issue **MUST** be communicated on all appropriate communication channels, including relevant community calls, chat channels and mailing lists. Comments of support from the community are welcome.
- The issue is approved and the proposed maintainer becomes a maintainer if either:
  - Two weeks have passed since at least three (3) Maintainer issue approvals have been recorded, OR
  - An absolute majority of maintainers have approved the issue.
- If the issue does not get the requisite approvals, it may be closed.
- Once the add maintainer issue has been approved, the necessary updates to the GitHub Teams are made via a PR to the Hyperledger "governance" repo's [access control file](https://github.com/hyperledger/governance/blob/main/access-control.yaml).

## Removing Maintainers

Being a maintainer is not a status symbol or a title to be carried
indefinitely. It will occasionally be necessary and appropriate to move a
maintainer to emeritus status. This can occur in the following situations:

- Resignation of a maintainer.
- Violation of the Code of Conduct warranting removal.
- Inactivity.
  - A general measure of inactivity will be no commits or code review comments
    for one reporting quarter. This will not be strictly enforced if
    the maintainer expresses a reasonable intent to continue contributing.
  - Reasonable exceptions to inactivity will be granted for known long term
    leave such as parental leave and medical leave.
- Other circumstances at the discretion of the other Maintainers.

The process to move a maintainer from active to emeritus status is comparable to the process for adding a maintainer, outlined above. In the case of voluntary
resignation, the Pull Request can be merged following a maintainer issue approval. If the removal is for any other reason, the following steps **SHOULD** be followed:

- An issue is created to move the maintainer to the list of emeritus maintainers.
- The issue is authored by, or has a comment supporting the proposal from, an existing maintainer or Hyperledger GitHub organization administrator.
- Once the issue and necessary comments have been received, the approval timeframe begins.
- The issue **MAY** be communicated on appropriate communication channels, including relevant community calls, chat channels and mailing lists.
- The issue is approved and the maintainer transitions to maintainer emeritus if:
  - The issue is approved by the maintainer to be transitioned, OR
  - Two weeks have passed since at least three (3) Maintainer issue approvals have been recorded, OR
  - An absolute majority of maintainers have approved the issue.
- If the issue does not get the requisite approvals, it may be closed.
- Once the remove maintainer issue has been approved, the necessary updates to the GitHub Teams are made via a PR to the Hyperledger "governance" repo's [access control file](https://github.com/hyperledger/governance/blob/main/access-control.yaml).

Returning to active status from emeritus status uses the same steps as adding a
new maintainer. Note that the emeritus maintainer already has the 5 required
significant changes as there is no contribution time horizon for those.
