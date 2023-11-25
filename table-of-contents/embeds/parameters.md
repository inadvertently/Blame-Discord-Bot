---
description: >-
  Here, you can find the supported types of parameters blame accepts. Other bots
  variables may not work on blame so, try to stick to what you see here :D
---

# ✍ Parameters

### What are parameters?

Parameters are special kind of `variables` that tell our program that we are trying to call in a method or argument. An example of this would be trying to ping a member who joined. You'd usually just ping them like so, `@member` . Well, in raw form this would look like `@member.mention` Lets get into adding these parameters.

### **Parameters must be separated with "$v"**

## title

```
(title: text)
```

{% tabs %}
{% tab title="Syntax" %}
```
(title: text)
```
{% endtab %}

{% tab title="Example" %}
```
(title: hey, we hope you're understanding this!)
```


{% endtab %}
{% endtabs %}

## description

```
(description: text)
```

{% tabs %}
{% tab title="Syntax" %}
```
(description: text)
```
{% endtab %}

{% tab title="Second Tab" %}
```
(description: this is how you add a description!)
```
{% endtab %}
{% endtabs %}

## color

```
(color: hex)
```

{% tabs %}
{% tab title="Syntax" %}
```
(color: hex)
```
{% endtab %}

{% tab title="Example" %}
```
(color: 000000)
```
{% endtab %}
{% endtabs %}

## author

```
(author: name && icon: URL)
```

{% tabs %}
{% tab title="Syntax" %}
```
(author: text && icon: URL)
```
{% endtab %}

{% tab title="Second Tab" %}
```
(author: hi docs && icon: https://blame.gg/assets/logo.png)
```
{% endtab %}
{% endtabs %}

## footer

```
(footer: text && icon: URL)
```

{% tabs %}
{% tab title="Syntax" %}
```
(footer: text && icon: URL)
```
{% endtab %}

{% tab title="Example" %}
```
(footer: hi again, docs && icon: https://blame.gg/assets/logo.png)
```


{% endtab %}
{% endtabs %}

## image

```
(image: URL)
```

{% tabs %}
{% tab title="Syntax" %}
<pre><code><strong>(image: URL)</strong></code></pre>
{% endtab %}

{% tab title="Example" %}
```
(image: https://blame.gg/assets/logo.png)
```
{% endtab %}
{% endtabs %}

## thumbnail

{% tabs %}
{% tab title="Syntax" %}
(thumbnail: URL)
{% endtab %}

{% tab title="Example" %}
(thumbnail: https://blame.gg/assets/logo.png)
{% endtab %}
{% endtabs %}
