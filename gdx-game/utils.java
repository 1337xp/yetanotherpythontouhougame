package com.aminedev.run;
import com.badlogic.gdx.graphics.*;
import com.badlogic.gdx.*;

public class utils
{
	public static void configureCamera(OrthographicCamera camera)
	{
		if (Gdx.graphics.getHeight() < Gdx.graphics.getWidth())
			camera.setToOrtho(false, 800, 800 * Gdx.graphics.getHeight() / Gdx.graphics.getWidth());
		else
			camera.setToOrtho(false, 800 * Gdx.graphics.getWidth() / Gdx.graphics.getHeight(), 800);
	}
}
