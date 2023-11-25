---
description: >-
  Supported content that you can include in your embeds parameter values!
  Anytime you use a variable its must be wrapped in curly brackets.
---

# 🔑 Variables

## User variables

These are supported variables within a member object

| variable           |              response             |     |
| ------------------ | :-------------------------------: | :-: |
| user               |       Name and discriminator      |     |
| user.mention       |         Mentions the user         |     |
| user.name          |    Returns the name of the user   |     |
| user.avatar        |   Returns the avatar of the user  |     |
| user.joined\_at    | Date the user joined the guild at |     |
| user.discriminator |           The users tag           |     |

## Guild Variables

These are supported variables within a guild (server).

| variable           |              response             |     |
| ------------------ | :-------------------------------: | :-: |
| guild.name         |       The name of the guild       |     |
| guild.count        |    The membercount of the guild   |     |
| guild.id           |        The id of the guild        |     |
| guild.created\_at  |  Return the guilds creation date  |     |
| guild.boost\_count | The guilds total number of boosts |     |
| guild.icon         |  Returns the avatar of the guild  |     |

## Basic Examples

1. **In this first example we're just going to create an embed that says "welcome" in the title and, the server name in the description.**

```
(embed)(title: welcome)$v(description: {guild.name})
```

#### 2. In this second example, we're going to welcome the user as up above, set their avatar as the thumbnail and add their username to the author.

```
(embed)(title: welcome)$v(description: {guild.name})$v(thumbnail: {user.avatar})$v(author: {user.name})
```
