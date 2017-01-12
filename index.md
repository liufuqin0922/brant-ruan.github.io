<ul>

  {% for post in site.categories.Poem %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

